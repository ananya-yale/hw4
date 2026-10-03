import { useEffect, useState, type FormEvent } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import ProductCard from "./ProductCard";
import { fetchChatHistory, sendChatMessage } from "../api";
import { useAuth } from "../AuthContext";
import { useSearchResults } from "../SearchResultsContext";
import type { ChatProductCard } from "../types";

interface ChatMessage {
  role: "assistant" | "user";
  content: string;
  products?: ChatProductCard[];
}

const WELCOME_MESSAGE: ChatMessage = {
  role: "assistant",
  content: "Hi! I'm the Campus Customs assistant. Ask me about products, sizes, or anything else!",
};

/** If the customer is on a product detail page, pull its id out of the URL
 * so the chat request can tell the agent what they're looking at. */
function useCurrentProductId(): string | null {
  const location = useLocation();
  const match = location.pathname.match(/^\/products\/([^/]+)$/);
  return match ? match[1] : null;
}

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([WELCOME_MESSAGE]);
  const [draft, setDraft] = useState("");
  const [sending, setSending] = useState(false);
  const { setResults } = useSearchResults();
  const { user } = useAuth();
  const navigate = useNavigate();
  const currentProductId = useCurrentProductId();

  useEffect(() => {
    if (!user) {
      setMessages([WELCOME_MESSAGE]);
      return;
    }
    fetchChatHistory(user.id)
      .then((history) => {
        if (history.length === 0) return;
        setMessages(
          history.map((entry) => ({
            role: entry.role,
            content: entry.content,
            products: entry.products,
          })),
        );
      })
      .catch(() => {
        // Keep the default welcome message if history can't be loaded.
      });
  }, [user]);

  async function handleSubmit(event: FormEvent) {
    event.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed || sending) return;

    setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
    setDraft("");
    setSending(true);

    try {
      const reply = await sendChatMessage(trimmed, user?.id ?? null, currentProductId);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: reply.reply, products: reply.products },
      ]);
      if (reply.products.length > 0) {
        setResults(reply.products, trimmed);
        navigate("/products");
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, I couldn't reach the chat service. Please try again." },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="chat-widget">
      {isOpen && (
        <div className="chat-panel">
          <div className="chat-header">
            <span>Campus Customs Chat</span>
            <button onClick={() => setIsOpen(false)} aria-label="Close chat">
              ×
            </button>
          </div>
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div key={index} className={`chat-message ${message.role}`}>
                {message.content}
                {message.products && message.products.length > 0 && (
                  <div className="chat-product-grid">
                    {message.products.map((product) => (
                      <ProductCard key={product.product_id} product={product} />
                    ))}
                  </div>
                )}
              </div>
            ))}
            {sending && <div className="chat-message assistant">Thinking...</div>}
          </div>
          <form className="chat-input-row" onSubmit={handleSubmit}>
            <input
              type="text"
              value={draft}
              onChange={(event) => setDraft(event.target.value)}
              placeholder="Type a message..."
              disabled={sending}
            />
            <button type="submit" disabled={sending}>
              Send
            </button>
          </form>
        </div>
      )}
      <button className="chat-toggle" onClick={() => setIsOpen((open) => !open)}>
        {isOpen ? "Close" : "Chat with us"}
      </button>
    </div>
  );
}

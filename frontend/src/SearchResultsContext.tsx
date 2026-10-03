import { createContext, useContext, useState, type ReactNode } from "react";
import type { ChatProductCard } from "./types";

/**
 * Holds the most recent chat-driven product search, so the Products page can
 * render those exact results as cards instead of (or in front of) the full
 * catalogue. This is the "API contract" surface on the frontend side: the
 * agent's ChatReply.products becomes this context's `results`, and any page
 * that reads this context re-renders with the new matches.
 */
interface SearchResultsValue {
  results: ChatProductCard[] | null;
  query: string | null;
  setResults: (results: ChatProductCard[], query: string) => void;
  clearResults: () => void;
}

const SearchResultsContext = createContext<SearchResultsValue | undefined>(undefined);

export function SearchResultsProvider({ children }: { children: ReactNode }) {
  const [results, setResultsState] = useState<ChatProductCard[] | null>(null);
  const [query, setQuery] = useState<string | null>(null);

  function setResults(products: ChatProductCard[], newQuery: string) {
    setResultsState(products);
    setQuery(newQuery);
  }

  function clearResults() {
    setResultsState(null);
    setQuery(null);
  }

  return (
    <SearchResultsContext.Provider value={{ results, query, setResults, clearResults }}>
      {children}
    </SearchResultsContext.Provider>
  );
}

export function useSearchResults(): SearchResultsValue {
  const ctx = useContext(SearchResultsContext);
  if (!ctx) throw new Error("useSearchResults must be used within a SearchResultsProvider");
  return ctx;
}

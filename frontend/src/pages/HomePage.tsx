import { Link } from "react-router-dom";
import FeatureIcon from "../components/FeatureIcon";

export default function HomePage() {
  return (
    <div>
      <section className="hero">
        <h1>Wear Your Yale, Your Way</h1>
        <p>
          From dorm days to decades-later tailgates, Campus Customs keeps you covered in gear
          that actually feels like home. Bulldog blue, loud and proud.
        </p>
        <Link to="/products" className="btn">
          Shop the Collection
        </Link>
      </section>

      <section className="section">
        <h2>Why Campus Customs</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <FeatureIcon name="people" />
            <h3>Built for Every Bulldog</h3>
            <p>
              Students, alumni, parents, and anyone who's ever cheered from the stands — we've
              got something in your size and your spirit.
            </p>
          </div>
          <div className="feature-card">
            <FeatureIcon name="shield" />
            <h3>Residential Colleges to Varsity Teams</h3>
            <p>
              Rep your college, your club sport, your major, or just the Bulldog itself.
              Campus pride comes in a lot of flavors.
            </p>
          </div>
          <div className="feature-card">
            <FeatureIcon name="hoodie" />
            <h3>Comfort That Lasts</h3>
            <p>
              Hoodies for late-night study sessions, tees for game day, fleece for the walk
              across Old Campus in February. Quality that keeps up with you.
            </p>
          </div>
        </div>
      </section>

      <section className="section" style={{ background: "var(--yale-blue-light)" }}>
        <h2>Find Your Fit</h2>
        <div className="feature-grid">
          <div className="feature-card">
            <FeatureIcon name="sparkle" />
            <h3>New Drops Weekly</h3>
            <p>Fresh designs land all the time, from throwback graphics to brand-new rivalry gear.</p>
          </div>
          <div className="feature-card">
            <FeatureIcon name="ruler" />
            <h3>Easy Sizing</h3>
            <p>Full size runs with live stock, so you know exactly what's available before you buy.</p>
          </div>
          <div className="feature-card">
            <FeatureIcon name="chat" />
            <h3>Questions? Just Ask</h3>
            <p>Our chat assistant in the corner is ready to help you track down the perfect piece.</p>
          </div>
        </div>
      </section>
    </div>
  );
}

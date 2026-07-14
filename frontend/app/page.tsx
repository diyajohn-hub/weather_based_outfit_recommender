"use client";

import { useState } from "react";

interface WeatherData {
  city: string;
  recommended_outfit: string;
  current_weather_metrics: {
    "apparent_temperature_max (°C)": number;
    "apparent_temperature_min (°C)": number;
    "precipitation_sum (mm)": number;
    "wind_speed_10m_max (km/h)": number;
  };
}

export default function Home() {
  const [city, setCity] = useState("");
  const [data, setData] = useState<WeatherData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const fetchRecommendation = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!city) return;

    setLoading(true);
    setError("");
    setData(null);

    try {
      // Fetching directly from your local Flask backend engine
      const res = await fetch(`http://127.0.0.1:5000/recommend?city=${city}`);
      if (!res.ok) throw new Error("City not found or server error");
      
      const result = await res.json();
      setData(result);
    } catch (err: any) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main style={{ padding: "2rem", fontFamily: "sans-serif", maxWidth: "600px", margin: "0 auto" }}>
      <h2>🌤️ AI Outfit Recommender</h2>
      
      <form onSubmit={fetchRecommendation} style={{ display: "flex", gap: "10px", marginBottom: "2rem" }}>
        <input
          type="text"
          placeholder="Enter city (e.g., Kottayam)"
          value={city}
          onChange={(e) => setCity(e.target.value)}
          style={{ padding: "10px", flex: 1, borderRadius: "5px", border: "1px solid #ccc" }}
        />
        <button type="submit" style={{ padding: "10px 20px", borderRadius: "5px", cursor: "pointer" }}>
          {loading ? "Analyzing..." : "Get Outfit"}
        </button>
      </form>

      {error && <p style={{ color: "red" }}>{error}</p>}

      {data && (
        <div style={{ padding: "1.5rem", border: "1px solid #eaeaea", borderRadius: "8px", backgroundColor: "#fafafa" }}>
          <h3>Location: {data.city}</h3>
          
          <div style={{ margin: "1rem 0", padding: "1rem", background: "#e0f7fa", borderRadius: "5px" }}>
            <strong>💡 Recommended Outfit:</strong>
            <p style={{ fontSize: "1.2rem", margin: "0.5rem 0 0 0" }}>{data.recommended_outfit}</p>
          </div>

          <h4>Today's Weather Metrics:</h4>
          <ul>
            <li>Max Feels Like: {data.current_weather_metrics["apparent_temperature_max (°C)"]}°C</li>
            <li>Min Feels Like: {data.current_weather_metrics["apparent_temperature_min (°C)"]}°C</li>
            <li>Precipitation: {data.current_weather_metrics["precipitation_sum (mm)"]} mm</li>
            <li>Max Wind Speed: {data.current_weather_metrics["wind_speed_10m_max (km/h)"]} km/h</li>
          </ul>
        </div>
      )}
    </main>
  );
}
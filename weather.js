
async function getWeather() {

    const latitude = 18.5204;
    const longitude = 73.8567;

    const url =
        `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,relative_humidity_2m,precipitation,rain,weather_code&timezone=Asia%2FKolkata`;

    try {
        const response = await fetch(url);

        if (!response.ok) {
            throw new Error("Weather API unavailable");
        }

        const data = await response.json();
        const current = data.current;

        document.getElementById("temperature").textContent =
            current.temperature_2m + " °C";

        document.getElementById("humidity").textContent =
            current.relative_humidity_2m + " %";

        document.getElementById("rainfall").textContent =
            current.precipitation + " mm";

        const codes = {
            0: "Clear ☀️",
            1: "Mostly Clear",
            2: "Partly Cloudy",
            3: "Cloudy ☁️",
            45: "Fog",
            48: "Fog",
            51: "Drizzle",
            61: "Rain 🌧️",
            63: "Rain",
            65: "Heavy Rain",
            80: "Rain Showers",
            95: "Thunderstorm ⚡"
        };

        document.getElementById("condition").textContent =
            codes[current.weather_code] || "Variable";

        document.getElementById("weatherMessage").textContent =
            "Weather data successfully fetched from Open-Meteo.";

    } catch (error) {

        document.getElementById("condition").textContent = "Unavailable";

        document.getElementById("weatherMessage").textContent =
            "Unable to load live weather. Check your internet connection.";
    }
}

getWeather();

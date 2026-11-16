
const crops = [
    {
        name: "Rice",
        soil: ["Clay", "Loamy"],
        water: ["High"],
        season: ["Monsoon"],
        duration: "120-150 days"
    },
    {
        name: "Wheat",
        soil: ["Loamy", "Clay"],
        water: ["Medium", "High"],
        season: ["Winter"],
        duration: "110-130 days"
    },
    {
        name: "Maize",
        soil: ["Loamy", "Sandy"],
        water: ["Medium", "High"],
        season: ["Monsoon", "Summer"],
        duration: "90-110 days"
    },
    {
        name: "Millet",
        soil: ["Sandy", "Loamy"],
        water: ["Low", "Medium"],
        season: ["Summer", "Monsoon"],
        duration: "75-100 days"
    },
    {
        name: "Cotton",
        soil: ["Clay", "Loamy"],
        water: ["Medium", "High"],
        season: ["Monsoon"],
        duration: "150-180 days"
    },
    {
        name: "Chickpea",
        soil: ["Loamy", "Sandy"],
        water: ["Low", "Medium"],
        season: ["Winter"],
        duration: "90-120 days"
    }
];

function recommendCrops() {

    const soil = document.getElementById("soil").value;
    const water = document.getElementById("water").value;
    const season = document.getElementById("season").value;

    const n = Number(document.getElementById("nitrogen").value);
    const p = Number(document.getElementById("phosphorus").value);
    const k = Number(document.getElementById("potassium").value);

    if ([n, p, k].some(v => !Number.isFinite(v) || v < 0 || v > 200) ||
        ["nitrogen", "phosphorus", "potassium"].some(id =>
            document.getElementById(id).value.trim() === "")) {

        alert("Please enter valid NPK values between 0 and 200.");
        return;
    }

    const results = crops.map(crop => {

        let score = 0;
        let reasons = [];

        if (crop.soil.includes(soil)) {
            score += 30;
            reasons.push("Suitable soil");
        }

        if (crop.water.includes(water)) {
            score += 25;
            reasons.push("Suitable water");
        }

        if (crop.season.includes(season)) {
            score += 30;
            reasons.push("Suitable season");
        }

        // Simple illustrative nutrient scoring
        const nutrientAverage = (n + p + k) / 3;

        if (nutrientAverage >= 20 && nutrientAverage <= 120) {
            score += 15;
            reasons.push("Nutrient values in selected range");
        }

        return {
            ...crop,
            score,
            reasons
        };
    });

    results.sort((a, b) => b.score - a.score);

    const topCrops = results.slice(0, 3);

    const container = document.getElementById("recommendations");

    container.innerHTML = topCrops.map((crop, index) => `
        <div class="crop-card">
            <h3>${index + 1}. ${crop.name}</h3>
            <div class="score">${crop.score}%</div>
            <p><b>Growing Duration:</b> ${crop.duration}</p>
            <p><b>Reasons:</b> ${crop.reasons.join(", ")}</p>
            <p><b>Suitability:</b> ${crop.score >= 70 ? "Good match" : crop.score >= 40 ? "Moderate match" : "Low match"}</p>
        </div>
    `).join("");

    updateCharts(n, p, k, topCrops);
}

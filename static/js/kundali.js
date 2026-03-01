// ================= SAFE FUNCTION =================
function safe(v){
    return (v === undefined || v === null || v === "") ? "-" : v;
}

// ================= EVENT LISTENER =================
document.addEventListener("DOMContentLoaded", function(){
    const btn = document.getElementById("generateBtn");
    if(btn){
        btn.addEventListener("click", generateKundali);
    }
});

// ================= MAIN FUNCTION =================
async function generateKundali(){

    // 1️⃣ Get input values
    const nameInput = document.getElementById("fullName").value.trim();
    const dobInput = document.getElementById("dob").value;
    const tobInput = document.getElementById("tob").value;
    const cityInput = document.getElementById("city").value.trim();

    if(!nameInput || !dobInput || !tobInput || !cityInput){
        alert("Please fill all fields");
        return;
    }

    // 2️⃣ Prepare payload
    const d = dobInput.split("-");
    const t = tobInput.split(":");

    const payload = {
        year: parseInt(d[0]),
        month: parseInt(d[1]),
        day: parseInt(d[2]),
        hour: parseInt(t[0]),
        minute: parseInt(t[1]),
        city: cityInput
    };

    try{

        // 3️⃣ Fetch API
        const res = await fetch("/api/kundali",{
            method:"POST",
            headers:{"Content-Type":"application/json"},
            body: JSON.stringify(payload)
        });

        if(!res.ok){
            console.error("Backend error");
            alert("Backend error");
            return;
        }

        // 4️⃣ Now data exists
        const data = await res.json();
        console.log("API DATA:", data);

        // ================= BIRTH DETAILS =================
        document.getElementById("displayName").innerText = nameInput;
        document.getElementById("displayDob").innerText = dobInput;
        document.getElementById("displayTob").innerText = tobInput;
        document.getElementById("displayCity").innerText = cityInput;

        document.getElementById("displayLagna").innerText = safe(data.lagna);

        // Moon Sign
        const moon = data.planets?.find(p => p.name === "Moon");
        document.getElementById("moonSign").innerText = safe(moon?.sign);

        // ================= PANCHANG =================
        document.getElementById("nakshatra").innerText = safe(data.nakshatra);
        document.getElementById("ayanamsa").innerText = safe(data.ayanamsa);
        document.getElementById("tithi").innerText = safe(data.tithi_name);
        document.getElementById("birthYoga").innerText = safe(data.yoga_number);
        document.getElementById("karana").innerText = safe(data.karana_number);


        // ================= UPDATE SVG =================

const shortNames = {
    Sun: "Su",
    Moon: "Mo",
    Mars: "Ma",
    Mercury: "Me",
    Jupiter: "Ju",
    Venus: "Ve",
    Saturn: "Sa",
    Rahu: "Ra",
    Ketu: "Ke",
    Lagna: "La"
};

// Clear old data
for (let i = 1; i <= 12; i++) {
    const el = document.getElementById("house" + i);
    if (el) el.textContent = "";
}

if (data.houses) {
    for (let i = 1; i <= 12; i++) {

        const el = document.getElementById("house" + i);

        if (el && data.houses[i]) {
            el.textContent =
                data.houses[i]
                    .map(p => shortNames[p] || p)
                    .join(" ");
        }
    }
}

// ================= UPDATE D9 SVG =================

if (data.d9_houses) {

    // Clear old data
    for (let i = 1; i <= 12; i++) {
        const el = document.getElementById("dhouse" + i);
        if (el) el.textContent = "";
    }

    for (let i = 1; i <= 12; i++) {

        const el = document.getElementById("dhouse" + i);

        if (el && data.d9_houses[i]) {
            el.textContent = data.d9_houses[i].join(" ");
        }
    }
}
        // ================= PLANET TABLE =================
        let table = "";

        if(data.planets && Array.isArray(data.planets)){
            data.planets.forEach(p=>{
                table += `
                <tr>
                    <td>${safe(p.name)}</td>
                    <td>${safe(p.sign)}</td>
                    <td>${safe(p.degree)}</td>
                    <td>${safe(p.house)}</td>
                    <td>-</td>
                    <td>-</td>
                    <td>${p.retrograde ? "Retrograde" : "Direct"}</td>
                </tr>`;
            });
        }

        document.getElementById("planetTable").innerHTML = table;

        // ================= HOUSE ANALYSIS =================
        let houseHTML = "";

        if(data.houses){
            for(const house in data.houses){
                const planets = data.houses[house];
                houseHTML += `
                <div class="mb-2">
                    <b>House ${house}:</b> 
                    ${planets.length ? planets.join(", ") : "-"}
                </div>`;
            }
        }

        document.getElementById("houseAnalysis").innerHTML = houseHTML;

        // ================= DASHAS (Future Ready) =================
        document.getElementById("dashaBalance").innerText = safe(data.dasha_balance);
        document.getElementById("mahadasha").innerText = safe(data.mahadasha);
        document.getElementById("antardasha").innerText = safe(data.antardasha);
        document.getElementById("dashaPeriod").innerText = safe(data.dasha_period);

        // ================= LIFE ANALYSIS =================
// After: const data = await response.json();
if (data.scores) {

  const setScore = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.innerText = value ?? 0;
  };

  setScore("careerScore", data.scores.career_score);
  setScore("financeScore", data.scores.finance_score);
  setScore("relationshipScore", data.scores.marriage_score);
  setScore("healthScore", data.scores.mental_score);
  setScore("overallScore", data.scores.overall_strength);
}
        // ================= YOGAS / DOSHAS =================
        if(data.yogas){
            document.getElementById("yogaList").innerHTML =
                data.yogas.map(y=>`<li>${y}</li>`).join("");
        }

        
        if(data.doshas){
            document.getElementById("doshaList").innerHTML =
                data.doshas.map(d=>`<li>${d}</li>`).join("");
        }

        if(data.remedies){
            document.getElementById("remedies").innerHTML =
                data.remedies.map(r=>`<li>${r}</li>`).join("");
        }

    }catch(err){
        console.error("Fetch error:", err);
        alert("Server error");
    }

    
}
// ================= CHAT FUNCTION =================

async function sendMessage(){

    const input = document.getElementById("chatInput");
    const message = input.value.trim();

    if(!message) return;

    const chatBox = document.getElementById("chatBox");

    // Show user message
    chatBox.innerHTML += `
        <div style="text-align:right; margin-bottom:10px;">
            <span style="background:#ffc107; color:#000; padding:8px 12px; border-radius:15px;">
                ${message}
            </span>
        </div>
    `;

    input.value = "";
    chatBox.scrollTop = chatBox.scrollHeight;

    try{

        const res = await fetch("/api/chat", {
            method: "POST",
            headers: {"Content-Type":"application/json"},
            body: JSON.stringify({
                message: message
            })
        });

        const data = await res.json();

        // Show AI response
        chatBox.innerHTML += `
            <div style="text-align:left; margin-bottom:10px;">
                <span style="background:#1c2e4a; color:#fff; padding:8px 12px; border-radius:15px;">
                    ${data.reply}
                </span>
            </div>
        `;

        chatBox.scrollTop = chatBox.scrollHeight;

    } catch(err){
        console.error("Chat error:", err);
    }
}
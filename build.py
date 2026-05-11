import urllib.request
import json
import sys
import os
import time
from datetime import datetime

def fetch_weather():
    lat = 56.59104
    lon = -3.34086
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,weather_code,wind_speed_10m,wind_gusts_10m&hourly=temperature_2m,precipitation_probability,weather_code,wind_speed_10m,wind_gusts_10m&daily=temperature_2m_max,temperature_2m_min,sunrise,sunset,precipitation_probability_max,weather_code,wind_speed_10m_max,wind_gusts_10m_max&timezone=Europe%2FLondon&forecast_days=3&wind_speed_unit=mph"
    
    req = urllib.request.Request(url, headers={'User-Agent': 'Synology-Weather-Bot'})
    
    max_retries = 5
    for attempt in range(max_retries):
        try:
            # 30-second timeout per attempt
            with urllib.request.urlopen(req, timeout=60) as response:
                return json.loads(response.read().decode('utf-8'))
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(5) # Wait 5 seconds before trying again
            else:
                raise e # If all 3 attempts fail, pass the error down to trigger the email

def build_html(weather_data):
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<title>Weather Now</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { width: 100vw; height: 100vh; background: #ffffff; font-family: sans-serif; overflow: hidden; display: flex; justify-content: center; align-items: center; }
  .kindle-wrapper { display: flex; justify-content: center; align-items: center; transform: none; transition: transform 0.3s ease; }
  @media screen and (max-width: 799px) { .kindle-wrapper { transform: rotate(-90deg) scale(0.92); transform-origin: center center; } }
  .container { width: 800px; height: 480px; background: #fff; color: #000; font: 400 16px Georgia, serif; display: flex; flex-direction: column; justify-content: space-between; padding: 25px 45px; text-rendering: optimizeLegibility; position: relative; overflow: hidden; -webkit-font-smoothing: antialiased; }
  .top-row { display: flex; justify-content: space-between; align-items: flex-start; }
  .col-left { width: 230px; }
  .col-center { flex: 1; text-align: center; }
  .col-right { width: 210px; text-align: right; }
  .loc { font-size: 28px; font-weight: bold; line-height: 1; }
  .sub-loc { font-size: 18px; margin-top: 2px; }
  .date-line { font-size: 12px; margin-top: 6px; display: block; }
  .sun { font-size: 12px; margin-top: 8px; border-top: 1px solid #000; display: inline-block; padding-top: 4px; white-space: nowrap; }
  .temp-big { font-size: 115px; line-height: .8; }
  .cond-big { font-size: 25px; margin-top: 5px; }
  .details { font-size: 17px; line-height: 1.6; }
  .flourish-swoosh { height: 22px; margin: 12px 0 6px auto; display: block; width: 60px; }
  .quote { font-size: 15px; line-height: 1.25; }
  .hourly-row { display: grid; grid-template-columns: repeat(5, 70px) 1fr; column-gap: 20px; border-top: 3px solid #000; border-bottom: 3px solid #000; padding: 10px 0; margin: 2px 0; }
  .h-col { text-align: center; }
  .later-col { text-align: left; padding-left: 10px; }
  .v-time { font-size: 16px; font-weight: bold; height: 18px; line-height: 18px; }
  .v-temp { font-size: 21px; margin: 2px 0; height: 25px; line-height: 25px; }
  .v-cond { font-size: 11px; height: 28px; margin-bottom: 0; line-height: 14px; display: block; overflow: hidden; } 
  .v-data { font-size: 11px; height: 14px; line-height: 14px; }
  .later-text { font-size: 11px; line-height: 14px; margin-top: 0; }
  .bottom-blocks { display: flex; flex-direction: column; }
  .info-block, .footer { font-size: 19px; line-height: 1.3; }
  .info-block { margin-bottom: 12px; }
</style>
</head>
<body>
<div class="kindle-wrapper">
  <div id="dashboard" class="container"></div>
</div>
<script>
const d = {{WEATHER_JSON}};

function getOrdinalNum(n) { const s = ["th", "st", "nd", "rd"]; const v = n % 100; return n + (s[(v - 20) % 10] || s[v] || s[0]); }
function formatAmPm(hour) { if (hour === 0) return "12am"; if (hour < 12) return hour + "am"; if (hour === 12) return "12pm"; return (hour - 12) + "pm"; }
function formatSunTime(isoStr) { const time = isoStr.split("T")[1]; let [h, m] = time.split(":"); h = parseInt(h); const ampm = h >= 12 ? 'pm' : 'am'; h = h % 12; if (h === 0) h = 12; return `${h}.${m}${ampm}`; }

function getCondString(code, isNight, wind, prob, format, temp) {
  if (format === 'hourly') {
    if (code >= 95) return "Thunder"; 
    if (prob >= 50) {
      if (code >= 71 && code <= 86 || code === 77) return "Snow";
      if (code >= 61 && code <= 67) return "Rain";
      if (code >= 80 && code <= 82) return "Showers";
      if (code >= 51 && code <= 57) return "Drizzle";
      return temp < 0 ? "Wintry showers" : "Showers";
    }
    if (code === 0) return isNight ? "Clear" : "Sunny"; if (code === 1) return isNight ? "Mostly clear" : "Mostly sunny"; if (code === 2) return "Partly cloudy"; if (code === 3) return "Cloudy"; if (code >= 71 && code <= 86) return "Snow"; if (code >= 61 && code <= 67) return "Rain"; if (code >= 80 && code <= 82) return "Showers"; if (code >= 51 && code <= 57) return "Drizzle"; if (wind > 20) return "Windy"; if (code === 45 || code === 48) return "Fog"; return "Cloudy";
  } else if (format === 'summary') {
    if (code >= 95) return "Thunder. "; 
    if (prob >= 50) {
      if (code >= 71 && code <= 86 || code === 77) return "Snowy. ";
      if (code >= 61 && code <= 67) return "Rainy. ";
      if (code >= 80 && code <= 82) return "Showery. ";
      if (code >= 51 && code <= 57) return "Drizzly. ";
      return temp < 0 ? "Wintry showers. " : "Showery. ";
    }
    if (code === 0) return isNight ? "Clear sky. " : "Sunny. "; if (code === 1) return isNight ? "Mostly clear. " : "Mostly sunny. "; if (code === 2) return "Partly cloudy. "; if (code === 45 || code === 48) return "Foggy. "; return "Cloudy. ";
  } else {
    if (code >= 95) return "Thunder"; 
    if (prob >= 50) {
      if (code >= 71 && code <= 86 || code === 77) return "Snow";
      if (code >= 61 && code <= 67) return "Rain";
      if (code >= 80 && code <= 82) return "Showers";
      if (code >= 51 && code <= 57) return "Drizzle";
      return temp < 0 ? "Wintry showers" : "Showers";
    }
    if (code === 0) return isNight ? "Clear sky" : "Sunny"; if (code === 1) return isNight ? "Mostly clear" : "Mostly sunny"; if (code === 2) return "Partly cloudy"; if (code === 3) return "Cloudy"; if (code >= 71 && code <= 86) return "Snow"; if (code === 77) return "Snow"; if (code >= 61 && code <= 67) return "Rain"; if (code >= 80 && code <= 82) return "Showers"; if (code >= 51 && code <= 57) return "Drizzle"; if (code === 45 || code === 48) return "Fog"; if (wind > 20) return "Windy"; return "Cloudy";
  }
}

function renderDashboard() {
  const now = new Date();
  const ukTime = new Date(now.toLocaleString("en-US", {timeZone: "Europe/London"}));
  
  const y = ukTime.getFullYear(); const m = String(ukTime.getMonth() + 1).padStart(2, '0'); const dStr = String(ukTime.getDate()).padStart(2, '0'); const hStr = String(ukTime.getHours()).padStart(2, '0');
  const targetHour = `${y}-${m}-${dStr}T${hStr}:00`; const targetDay = `${y}-${m}-${dStr}`;
  let hr_now = d.hourly.time.indexOf(targetHour); let day_now = d.daily.time.indexOf(targetDay);
  if (hr_now === -1) hr_now = ukTime.getHours(); 
  if (day_now === -1) day_now = 0;

  const current_h_int = ukTime.getHours(); const endOfDayIdx = hr_now + (23 - current_h_int); 
  const cur_p = d.hourly.precipitation_probability[hr_now]; const cur_c = d.current.weather_code; const cur_w = d.current.wind_speed_10m; const cur_g = d.current.wind_gusts_10m; const cur_t = Math.round(d.current.temperature_2m);
  const sunset_hr = parseInt(d.daily.sunset[day_now].split("T")[1].split(":")[0]); const sunrise_hr = parseInt(d.daily.sunrise[day_now].split("T")[1].split(":")[0]);
  const isNight = current_h_int >= sunset_hr || current_h_int < sunrise_hr;

  const days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  const months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  const dateString = `${days[ukTime.getDay()]}, ${months[ukTime.getMonth()]} ${getOrdinalNum(ukTime.getDate())}, ${ukTime.getFullYear()}`;

  const condBig = getCondString(cur_c, isNight, cur_w, cur_p, 'big', cur_t);
  let rainStr = cur_p === 0 ? "Dry" : `${(cur_c >= 71 && cur_c <= 86) ? 'Snow' : (cur_c >= 95 ? 'Hail' : 'Rain')}: ${cur_p}%`;
  let windStr = cur_g < 10 ? "Calm" : `Wind: ${Math.round(cur_w)}/${Math.round(cur_g)}mph`;

  let hourlyHTML = "";
  for (let i = 1; i <= 5; i++) {
    const idx = hr_now + i; const hp = d.hourly.precipitation_probability[idx]; const hc = d.hourly.weather_code[idx]; const ht = Math.round(d.hourly.temperature_2m[idx]); const hw = d.hourly.wind_speed_10m[idx]; const hg = d.hourly.wind_gusts_10m[idx];
    const hi = parseInt(d.hourly.time[idx].split("T")[1].split(":")[0]); const hIsNight = hi >= sunset_hr || hi < sunrise_hr;
    const hCond = getCondString(hc, hIsNight, hw, hp, 'hourly', ht); const hRain = hp === 0 ? "Dry" : `Rain: ${hp}%`; const hWind = hg < 10 ? "Calm" : `${Math.round(hw)}/${Math.round(hg)}mph`; const hTime = formatAmPm(hi);
    hourlyHTML += `<div class="h-col"><div class="v-time">${hTime}</div><div class="v-temp">${ht}°</div><div class="v-cond">${hCond}</div><div class="v-data">${hRain}</div><div class="v-data">${hWind}</div></div>`;
  }

  let laterHTML = "";
  if (current_h_int >= 18) { laterHTML = `<div class="v-time">Sleep well</div>`; } else {
    const scanStart = hr_now + 6; let fMax = -99; for (let k = scanStart; k <= endOfDayIdx; k++) { if (d.hourly.temperature_2m[k] > fMax) fMax = d.hourly.temperature_2m[k]; }
    let uLow = 99; const scanEnd = hr_now + 18; for (let k = scanStart; k <= scanEnd; k++) { if (d.hourly.temperature_2m[k] < uLow) uLow = d.hourly.temperature_2m[k]; }
    const r_fMax = Math.round(fMax); const r_tMax = Math.round(d.daily.temperature_2m_max[day_now]);
    const tempDisplay = (r_fMax >= r_tMax) ? `${r_tMax}°/${Math.round(uLow)}°` : `${Math.round(uLow)}°`;

    let lmp = 0, lc = 99, lwm = 0, lgm = 0; 
    let lphRes = -1, lphCode = 0, lphTemp = 0;
    let lphEndRes = -1, lphIntermittent = false, lInRain = false;
    
    for (let j = scanStart; j <= endOfDayIdx; j++) {
      let p = d.hourly.precipitation_probability[j]; if (p > lmp) lmp = p;
      
      if (p >= 50) {
        if (lphRes === -1) { 
          lphRes = parseInt(d.hourly.time[j].split("T")[1].split(":")[0]); 
          lphCode = d.hourly.weather_code[j]; 
          lphTemp = d.hourly.temperature_2m[j]; 
          lInRain = true;
        } else if (!lInRain) {
          lphIntermittent = true;
        }
      } else {
        if (lInRain) {
          lInRain = false;
          if (lphEndRes === -1) lphEndRes = parseInt(d.hourly.time[j].split("T")[1].split(":")[0]);
        }
      }
      
      if (d.hourly.weather_code[j] < lc) lc = d.hourly.weather_code[j]; 
      if (d.hourly.wind_speed_10m[j] > lwm) lwm = d.hourly.wind_speed_10m[j]; 
      if (d.hourly.wind_gusts_10m[j] > lgm) lgm = d.hourly.wind_gusts_10m[j];
    }
    
    let laterSum = getCondString(lc, true, lwm, lmp, 'summary', uLow);
    if (lphRes !== -1) { 
      let type = "Showers"; 
      if (lphCode >= 71 && lphCode <= 86 || lphCode === 77) type = "Snow"; 
      else if (lphCode >= 61 && lphCode <= 67) type = "Rain"; 
      else if (lphCode >= 80 && lphCode <= 82) type = "Showers"; 
      else if (lphCode >= 51 && lphCode <= 57) type = "Drizzle"; 
      else if (lphTemp < 0) type = "Wintry showers"; 
      
      if (lphIntermittent) {
          laterSum += `Intermittent ${type.toLowerCase()} starting at ${formatAmPm(lphRes)}. `;
      } else if (lInRain || lphEndRes === -1) {
          laterSum += `${type} starting at ${formatAmPm(lphRes)}. `;
      } else {
          laterSum += `${type} at ${formatAmPm(lphRes)} until ${formatAmPm(lphEndRes)}. `;
      }
    } else { laterSum += `Likely dry. `; }
    laterSum += lgm < 10 ? `Probably calm.` : `Winds ${Math.round(lwm)}/${Math.round(lgm)}mph.`;
    laterHTML = `<div class="v-time">Later</div><div class="v-temp">${tempDisplay}</div><div class="later-text">${laterSum}</div>`;
  }

  let nLow = 100, nWi = 0, nGu = 0, nMp = 0; 
  let nPhRes = -1, nPhCode = 0, nPhTemp = 0;
  let nPhEndRes = -1, nPhIntermittent = false, nInRain = false;
  
  const nightStartIdx = endOfDayIdx - 1; const nightEndIdx = endOfDayIdx + 7;   
  for (let j = nightStartIdx; j <= nightEndIdx; j++) {
    if (j >= hr_now) {
      if (d.hourly.temperature_2m[j] < nLow) nLow = d.hourly.temperature_2m[j]; 
      if (d.hourly.wind_speed_10m[j] > nWi) nWi = d.hourly.wind_speed_10m[j]; 
      if (d.hourly.wind_gusts_10m[j] > nGu) nGu = d.hourly.wind_gusts_10m[j];
      
      let p = d.hourly.precipitation_probability[j]; if (p > nMp) nMp = p;
      
      if (p >= 50) {
        if (nPhRes === -1) { 
          nPhRes = parseInt(d.hourly.time[j].split("T")[1].split(":")[0]); 
          nPhCode = d.hourly.weather_code[j]; 
          nPhTemp = d.hourly.temperature_2m[j]; 
          nInRain = true;
        } else if (!nInRain) {
          nPhIntermittent = true;
        }
      } else {
        if (nInRain) {
          nInRain = false;
          if (nPhEndRes === -1) nPhEndRes = parseInt(d.hourly.time[j].split("T")[1].split(":")[0]);
        }
      }
    }
  }
  const midnightIdx = endOfDayIdx + 1; const nightC = d.hourly.weather_code[midnightIdx]; let nightCond = "cloudy";
  if (nMp >= 50) {
    if (nPhCode >= 71 && nPhCode <= 86 || nPhCode === 77) nightCond = "snowy";
    else if (nPhCode >= 61 && nPhCode <= 67) nightCond = "rainy";
    else if (nPhCode >= 80 && nPhCode <= 82) nightCond = "showery";
    else if (nPhCode >= 51 && nPhCode <= 57) nightCond = "drizzly";
    else nightCond = nLow < 0 ? "wintry showers" : "showery";
  } else if (nightC === 0) nightCond = "clear"; else if (nightC === 1) nightCond = "mostly clear"; else if (nightC === 2) nightCond = "partly cloudy"; else if (nightC === 45 || nightC === 48) nightCond = "foggy";
  
  let overHTML = `Likely ${nightCond}. Lows of ${Math.round(nLow)}°. `;
  if (nPhRes !== -1) { 
    let type = "Showers"; 
    if (nPhCode >= 71 && nPhCode <= 86 || nPhCode === 77) type = "Snow"; 
    else if (nPhCode >= 61 && nPhCode <= 67) type = "Rain"; 
    else if (nPhCode >= 80 && nPhCode <= 82) type = "Showers"; 
    else if (nPhCode >= 51 && nPhCode <= 57) type = "Drizzle"; 
    else if (nPhTemp < 0) type = "Wintry showers"; 
    
    if (nPhIntermittent) {
        overHTML += `Intermittent ${type.toLowerCase()} starting at ${formatAmPm(nPhRes)}. `;
    } else if (nInRain || nPhEndRes === -1) {
        overHTML += `${type} starting at ${formatAmPm(nPhRes)}. `;
    } else {
        overHTML += `${type} at ${formatAmPm(nPhRes)} until ${formatAmPm(nPhEndRes)}. `;
    }
  } else { overHTML += `Likely dry. `; }
  overHTML += nGu < 10 ? `Probably calm.` : `Winds ${Math.round(nWi)}/${Math.round(nGu)}mph.`;

  const tomIdx = day_now + 1; const tomTc = d.daily.weather_code[tomIdx];
  let tMax = -99, tMin = 99, tomWi = 0, tomGu = 0; 
  let tomPhRes = -1, tomPhCode = 0, tomPhTemp = 0; 
  let tomPhEndRes = -1, tomPhIntermittent = false, tomInRain = false;
  let daylightRainCount = 0, daylightSnowCount = 0;
  
  const tomStartIdx = endOfDayIdx + 7; const tomEndIdx = endOfDayIdx + 24; const daylightEndIdx = endOfDayIdx + 19; 
  for (let j = tomStartIdx; j <= tomEndIdx; j++) {
    let ht = d.hourly.temperature_2m[j]; if (ht > tMax) tMax = ht; if (ht < tMin) tMin = ht;
    let hw = d.hourly.wind_speed_10m[j]; if (hw > tomWi) tomWi = hw; let hg = d.hourly.wind_gusts_10m[j]; if (hg > tomGu) tomGu = hg;
    
    let p = d.hourly.precipitation_probability[j];
    if (p >= 50) {
      if (tomPhRes === -1) { 
        tomPhRes = parseInt(d.hourly.time[j].split("T")[1].split(":")[0]); 
        tomPhCode = d.hourly.weather_code[j]; 
        tomPhTemp = d.hourly.temperature_2m[j]; 
        tomInRain = true;
      } else if (!tomInRain) {
        tomPhIntermittent = true;
      }
    } else {
      if (tomInRain) {
        tomInRain = false;
        if (tomPhEndRes === -1) tomPhEndRes = parseInt(d.hourly.time[j].split("T")[1].split(":")[0]);
      }
    }
    
    if (j <= daylightEndIdx && p >= 50) { daylightRainCount++; let hc = d.hourly.weather_code[j]; if (hc >= 71 && hc <= 86) daylightSnowCount++; }
  }
  tMax = Math.round(tMax); tMin = Math.round(tMin);
  let tomCond = "Cloudy.";
  if (tomTc >= 95) tomCond = "Thunder."; 
  else if (daylightRainCount >= 3) {
    if (daylightSnowCount > 0) tomCond = "Snowy.";
    else if (tomTc >= 61 && tomTc <= 67) tomCond = "Rainy.";
    else if (tomTc >= 80 && tomTc <= 82) tomCond = "Showery.";
    else if (tomTc >= 51 && tomTc <= 57) tomCond = "Drizzly.";
    else tomCond = tMin < 0 ? "Wintry showers." : "Showery.";
  } else if (tomTc === 0) tomCond = "Sunny."; else if (tomTc === 1) tomCond = "Mostly sunny."; else if (tomTc === 2) tomCond = "Partly cloudy."; else if (tomTc === 45 || tomTc === 48) tomCond = "Foggy.";
  
  let tomStr = `${tomCond} Highs of ${tMax}°, lows of ${tMin}°. `;
  if (tomPhRes !== -1) { 
    let type = "showers"; 
    if (tomPhCode >= 71 && tomPhCode <= 86 || tomPhCode === 77) type = "snow"; 
    else if (tomPhCode >= 61 && tomPhCode <= 67) type = "rain"; 
    else if (tomPhCode >= 80 && tomPhCode <= 82) type = "showers"; 
    else if (tomPhCode >= 51 && tomPhCode <= 57) type = "drizzle"; 
    else if (tomPhTemp < 0) type = "wintry showers"; 
    
    if (tomPhIntermittent) {
        tomStr += `Expect intermittent ${type} starting at ${formatAmPm(tomPhRes)}. `;
    } else if (tomInRain || tomPhEndRes === -1) {
        tomStr += `Expect ${type} starting at ${formatAmPm(tomPhRes)}. `;
    } else {
        tomStr += `Expect ${type} at ${formatAmPm(tomPhRes)} until ${formatAmPm(tomPhEndRes)}. `;
    }
  } else { tomStr += `Likely dry. `; }
  tomStr += tomGu < 10 ? `Probably calm.` : `Winds ${Math.round(tomWi)}/${Math.round(tomGu)}mph.`;

  document.getElementById('dashboard').innerHTML = `
    <div class="top-row">
      <div class="col-left"><div class="loc">Weather now</div><div class="sub-loc">Blairgowrie</div><div class="date-line">${dateString}</div><div class="sun">Sunrise ${formatSunTime(d.daily.sunrise[day_now])} <span style="font-size: 10px; margin: 0 1px;">&#9728;&#xFE0E;</span> Sunset ${formatSunTime(d.daily.sunset[day_now])}</div></div>
      <div class="col-center"><div class="temp-big">${cur_t}°</div><div class="cond-big">${condBig}</div></div>
      <div class="col-right"><div class="details"><div>${rainStr}</div><div>${windStr}</div><svg class="flourish-swoosh" viewBox="0 0 100 30" preserveAspectRatio="none"><path d="M0,15 C20,35 40,-5 60,15 C80,35 100,-5 120,15" stroke="black" stroke-width="3.5" fill="none" stroke-linecap="round"/></svg><div class="quote">‘Inspiration is the<br>Temple of Quest’</div></div></div>
    </div>
    <div class="hourly-row">${hourlyHTML}<div class="later-col">${laterHTML}</div></div>
    <div class="bottom-blocks"><div class="info-block"><b>Overnight:</b> ${overHTML}</div><div class="footer"><b>Tomorrow:</b> ${tomStr}</div></div>
  `;
}
renderDashboard();
</script>
</body>
</html>"""
    
    final_html = html_template.replace("{{WEATHER_JSON}}", json.dumps(weather_data))
    
    # Absolute path to save the HTML
    with open("/var/services/homes/alex/scripts/weathernow/index.html", "w", encoding="utf-8") as file:
        file.write(final_html)

if __name__ == "__main__":
    try:
        data = fetch_weather()
        build_html(data)
    except Exception as e:
        base_path = "/var/services/homes/alex/scripts/weathernow"
        log_dir = os.path.join(base_path, "logs")

        # Create logs folder if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # Generate unique timestamped log
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        log_filename = f"error_{timestamp}.txt"
        with open(os.path.join(log_dir, log_filename), "w") as f:
            f.write(f"Python failed with error: {e}")

        # Overwrite the 'current' error for the Synology email body
        with open(os.path.join(base_path, "python_error.txt"), "w") as f:
            f.write(f"Python failed with error: {e}")

        sys.exit(1)
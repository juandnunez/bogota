# iPhone LTE on ETB (Bogotá)

Runbook to get an iPhone on ETB 4G/LTE data. Do the steps in order. Stop at the first step that fixes it.

## 0. Facts

| Item | Value |
|---|---|
| Data APN (current) | `internetmovil.etb.net.co` |
| Username / Password | blank / blank |
| Legacy APN (only if current one fails) | `moviletb.net.co`, user `etb`, pass `etb` |
| PLMN (MCC-MNC) | 732-187 |
| Own LTE band | Band 4 (AWS 1700/2100) in Bogotá |
| Outside ETB coverage | national roaming on partner network (voice/SMS/data), automatic |
| Activation IVR | dial `*750` with the SIM inserted |
| Minimum iOS | 8.1+ (any current iPhone is fine) |

Every iPhone sold since the iPhone 5 supports Band 4, so hardware is not the blocker.

## 1. SIM / eSIM active

Physical SIM:
1. Insert SIM, power cycle.
2. Dial `*750`, follow the voice menu (needs your cédula number).
3. Wait for the "línea activa" SMS. Until it arrives, nothing below will work.

eSIM:
1. Buy the eSIM from ETB (tienda.etb.com or a CEGA center). They send a QR.
2. Settings > Cellular > Add eSIM > Use QR Code. Scan.
3. Label the line "ETB". If you have two lines, set Cellular Data to ETB.
4. Dial `*750` from the ETB line if data still shows nothing after 10 min.

Check: Settings > Cellular > the ETB line shows "On" and the status bar shows "ETB".

## 2. Carrier settings + LTE mode

1. Settings > General > About. If a "Carrier Settings Update" prompt appears, tap Update.
2. Settings > Cellular > (ETB line) > Voice & Data > **LTE**. Not 5G Auto: ETB has no 5G spectrum, so 5G only appears via the roaming partner and adds handoff churn. Turn **VoLTE On**, then place one test call. If the call fails, ETB support (3777777) must enable VoLTE on the line.
3. Settings > Cellular > (ETB line) > Data Roaming > **On**. ETB uses national roaming in areas without its own Band 4 sites; with roaming off you lose data the moment you leave ETB coverage.
4. Toggle Airplane Mode on/off.

Most SIMs auto-provision the APN here. If the status bar shows LTE and Safari loads, stop. Done.

## 3. APN (only if data still dead)

Path A, manual:
1. Settings > Cellular > (ETB line) > Cellular Data Network.
2. Under **Cellular Data**: APN `internetmovil.etb.net.co`, Username blank, Password blank.
3. Leave Personal Hotspot APN blank (inherits) or set the same value.
4. Back out, Airplane Mode on/off.

Path B, profile (use when "Cellular Data Network" is hidden, which happens on some carrier-provisioned SIMs):
1. On a Mac/PC: `python3 iphone-lte-etb/make_profile.py` (file already committed as `ETB-LTE.mobileconfig`).
2. AirDrop or email `ETB-LTE.mobileconfig` to the iPhone and open it.
3. Settings > General > VPN & Device Management > "ETB LTE (Colombia)" > Install.
4. Airplane Mode on/off.

Fallback: regenerate with `--legacy` (APN `moviletb.net.co`, etb/etb) if the current APN gets rejected on an old SIM.

## 4. Still no data

Work through in order, test after each:
1. Settings > General > Transfer or Reset iPhone > Reset > **Reset Network Settings**. Re-enter Wi-Fi passwords afterwards. Redo step 3.
2. Confirm the plan actually includes data: dial `*611` or check the Mi ETB app. A voice-only or unpaid plan shows LTE with no throughput.
3. Confirm the phone is carrier-unlocked: Settings > General > About > Carrier Lock must read "No SIM restrictions".
4. Try the SIM in another phone. If it works there, the iPhone needs a carrier-settings reset (step 4.1) or the profile (step 3B). If it fails there too, the line is the problem: ETB support 3777777 (Bogotá) or a CEGA center.

## 5. Verify

- Status bar: "ETB" + "LTE" (or "4G").
- Settings > Cellular > Cellular Data Network shows the APN above.
- Speed test on LTE > 5 Mbps down means you are on ETB Band 4, not 3G fallback.
- Field Test (dial `*3001#12345#*`) > LTE > Serving Cell Info: band should read 4 inside Bogotá.

## Verified

2026-09-19, iPhone 17 Pro Max, iOS 26.6.2, physical SIM, carrier bundle 70.0: LTE up on ETB 4G with the APN above auto-provisioned in Cellular Data, LTE Setup, and Personal Hotspot. MMS fields left blank. Steps 1 and 2 were enough; the profile in step 3B was not needed.

## Optimize (after LTE works)

Ranked by payoff.

1. **Wi-Fi Calling On.** Settings > Cellular > ETB line > Wi-Fi Calling. Band 4 penetrates buildings badly; indoors this is what keeps calls up. Toggle missing means ETB has not enabled it on the line.
2. **Encrypted DNS.** `python3 make_profile.py --dns cloudflare -o ETB-LTE-DNS.mobileconfig` (or `--dns quad9`), install the same way as step 3B. Replaces carrier DNS with DNS-over-HTTPS on cellular and Wi-Fi.
3. **Stop background data bleed.** Settings > Cellular: cut Photos, App Store, media-sync apps. Settings > General > Background App Refresh > Wi-Fi. ETB plans are capped.
4. **Hotspot.** Personal Hotspot > Maximize Compatibility Off (5 GHz for laptops). Allow Others to Join Off.
5. **Network Selection: leave Automatic.** Pinning ETB manually disables national roaming outside Band 4 coverage.
6. **Signal audit.** Field Test > LTE > Serving Cell > RSRP. Above -100 dBm good. Below -110 dBm at a fixed location means Wi-Fi Calling is mandatory there.
7. **eSIM migration.** Move ETB to eSIM to free the physical slot for a travel SIM. Then set Allow Cellular Data Switching Off so the foreign SIM never bills background data.

Ceiling: ETB owns 30 MHz on Band 4. Real-world 20 to 60 Mbps. Past that, the network is the limit.

## Files

- `make_profile.py`: builds the `.mobileconfig` APN profile (deterministic UUIDs, so reinstalling replaces instead of duplicating). `--dns cloudflare|quad9` adds an encrypted-DNS payload.
- `ETB-LTE.mobileconfig`: the generated profile, ready to install.

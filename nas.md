Cool — I can put together **three concrete build options (low-cost / balanced / “future-proof”)** for a 6-disk RAIDZ-2 DIY NAS, with actual example parts (chassis, motherboard/CPU, PSU, RAM, and disks). I pick components that are reasonably available in Europe. Prices fluctuate, but this gives you a good ballpark.

---

## 🛠️ Build Options Overview

* **Build 1 — “Budget / Entry-Level”**: minimal cost, good for backups, media, light usage.
* **Build 2 — “Balanced / Home-Lab”**: better RAM, PSU, slightly more reliable / flexible.
* **Build 3 — “Future-Proof / Performance-Oriented”**: aiming for long-term, expandability, possibly heavier workloads (docker, VMs, many users).

---

## ✅ Build 1 — Budget / Entry-Level NAS

### [6‑Bay NAS Chassis (6 HDD bays)]()

#### Chasis 6 bahías

*€82.39*

### [WD Red Plus 2TB NAS HDD]()

#### 2TB HDD

*€96.99*

### [WD Red Plus 2TB NAS HDD]()

#### 2TB HDD

*€96.99*

### [WD Red Plus 2TB NAS HDD]()

#### 2TB HDD

*€96.99*

### [WD Red Plus 2TB NAS HDD]()

#### 2TB HDD

*€96.99*

### [WD Red Plus 2TB NAS HDD]()

#### 2TB HDD

*€96.99*

### [WD Red Plus 2TB NAS HDD]()

#### 2TB HDD

*€96.99*

### [Be Quiet! Pure Power 11 500W 80PLUS Gold PSU]()

#### PSU decente

*€116.56*

### Key parts & rationale

* **[6‑Bay NAS Chassis (6 HDD bays)]()** — a simple chassis with room for 6 drives, sufficient for a 6-disk RAIDZ-2. Good as a base for a small home-NAS.
* **6 × [WD Red Plus 2TB NAS HDD]()** — gives you ~8 TB usable after RAIDZ-2 (raw ~12 TB). Great for backups, media, documents. 2 TB drives minimize rebuild time and cost.
* **[Be Quiet! Pure Power 11 500W 80PLUS Gold PSU]()** — provides stable and efficient power, over-provisioned for 6 HDDs + basic motherboard/CPU. Good efficiency and reliability, important for 24/7 NAS.

**✅ What this build is good for:** personal backups, media (photos, videos), light file-server, maybe a couple of docker services.
**⚠️ Limitations:** modest total capacity (~8 TB usable), performance is basic, future expansion limited if you want more data.

---

## ⚖️ Build 2 — Balanced / Home-Lab NAS

### [Fractal Design Define 7 Mid‑Tower Case]()

#### Case ATX

*€177.28*

### [Kingston 16GB DDR4-3200 ECC Unbuffered DIMM]()

#### RAM ECC 16GB

*€218.00*

### [10Gtek 12G Internal PCI-E SAS/SATA HBA Controller Card]()

#### HBA SATA/SAS

*€77.99*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### Key parts & rationale

* **[Fractal Design Define 7 Mid‑Tower Case]()** — spacious chassis, good for future upgrades or additional drives, good cooling/airflow, quiet operation, well-suited for a 6-bay (or more) NAS.
* **[Kingston 16GB DDR4-3200 ECC Unbuffered DIMM]()** — ECC RAM improves data integrity, useful especially if you use ZFS and want reliability over long time. ~16 GB gives headroom for caching, snapshots, maybe light VMs or containers. ([SilverPC Blog][1])
* **[10Gtek 12G Internal PCI-E SAS/SATA HBA Controller Card]()** — gives enough ports for all 6 HDDs (and more later), exposing disks directly to OS (recommended for ZFS). ([SilverPC Blog][2])
* **6 × [Seagate IronWolf 6TB NAS HDD]()** — gives ~16–17 TB usable after RAIDZ-2 (raw ~24–26 TB), a good balance of storage capacity and long-term viability.

**✅ What this build is good for:** Larger home-lab use: media libraries, backups, docker containers, maybe a few VMs, a home cloud, moderate network storage demands. More room to grow than Build 1.
**⚠️ Tradeoffs:** higher initial cost and slightly more complex (needs HBA, ECC-compatible motherboard).

---

## 🧠 Build 3 — Future-Proof / Performance-Oriented NAS

### [Phanteks Enthoo Pro Midi-Tower Case]()

#### Case grande expandible

*€164.25*

### [Kingston 16GB DDR4-3200 ECC Unbuffered DIMM]()

#### RAM ECC 16GB

*€218.00*

### [LSI 9300-16i SAS/SATA HBA Controller Card]()

#### HBA SAS/SATA 16‑port

*€48.21*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### [Seagate IronWolf 6TB NAS HDD]()

#### 6TB HDD

*€109.90*

### Key parts & rationale

* **[Phanteks Enthoo Pro Midi-Tower Case]()** — robust, roomy case that supports many drives and expansion, good airflow — ideal if you foresee expanding beyond 6 disks or adding more hardware (cache SSDs, NIC, ...).
* **[Kingston 16GB DDR4-3200 ECC Unbuffered DIMM]()** — ECC memory crucial if you want maximum data integrity for a “mission-critical” NAS. Enough RAM to handle ZFS, multiple services, containers/VMs.
* **[LSI 9300-16i SAS/SATA HBA Controller Card]()** — enterprise-grade HBA, ideal for many drives, future expandability, and rock-solid compatibility with ZFS. Better than cheap SATA expansion cards for reliability. ([TrueNAS Community Forums][3])
* **6 × [Seagate IronWolf 6TB NAS HDD]()** — same as Build 2, but this build pairs the drives with more robust hardware and expansion potential, so you can scale later (cache SSDs, more disks, NIC upgrades).

**✅ What this build is good for:** Long-term storage server, home-lab, media + backups + maybe heavier workloads (many docker services, VMs, even future expansion to 8–10 drives). Future-proof and robust in terms of reliability and scalability.
**⚠️ Tradeoffs:** Highest upfront cost; more overkill if your needs are simple backups or occasional file sharing.

---

## 📝 Some Commentary and Advice (based on experience + community wisdom)

* Using an **HBA / SAS-SATA controller** (like the ones in Builds 2 & 3) rather than relying only on motherboard’s SATA ports is often recommended for DIY-NAS setups with many drives — especially if you run ZFS — because the OS needs direct access to disks. ([SilverPC Blog][2])
* **ECC RAM** is a “nice to have” but not strictly mandatory — many successful home NAS builds are done with non-ECC RAM, especially if budget is the main concern. ([SilverPC Blog][1])
* Leave one SATA/HBA port free if you plan to add a **small SSD for OS (boot+system)** rather than putting the system on one of the data disks. That way your pool remains dedicated solely to data. ([SilverPC Blog][4])
* Make sure the chassis has good **airflow and cooling** — multiple spinning HDDs (especially larger ones) generate heat, and for long-term reliability, cooling matters. ([SilverPC Blog][5])

---

If you like — I can **prepare 2 extra builds** as **“silent / low-power”** (for a NAS in living room) and **“performance + 10 GbE network”** (for fast LAN transfers) — so you have **5 total build options**.
Do you want me to build those too now?

[1]: https://blog.silverpc.hu/2025/09/19/la-guia-definitiva-para-montar-un-nas-casero-desde-cero/?utm_source=chatgpt.com "La Guía Definitiva para Montar un NAS Casero desde Cero - SilverPC Blog"
[2]: https://blog.silverpc.hu/2025/09/16/todo-lo-que-necesitas-saber-sobre-los-componentes-para-un-nas-casero/?utm_source=chatgpt.com "Todo lo que necesitas saber sobre los componentes para un NAS casero - SilverPC Blog"
[3]: https://forums.truenas.com/t/feedback-on-my-planned-nas-build-xeon-ecc/49437?utm_source=chatgpt.com "Feedback on my planned NAS build (Xeon + ECC) - TrueNAS General - TrueNAS Community Forums"
[4]: https://blog.silverpc.hu/2025/09/21/monta-tu-propio-pc-para-nas-y-media-center-casero-guia-de-componentes/?utm_source=chatgpt.com "Monta tu propio PC para NAS y Media Center casero: Guía de componentes - SilverPC Blog"
[5]: https://blog.silverpc.hu/2025/09/22/nas-casero-la-guia-definitiva-sobre-que-componentes-y-software-montar/?utm_source=chatgpt.com "NAS casero: La guía definitiva sobre qué componentes y software montar - SilverPC Blog"


Perfect — here are **two additional NAS build options**, designed to complement the first three:

* **Build 4 → Silent / Low-Power NAS** (ideal for living room, bedroom, or 24/7 efficiency)
* **Build 5 → Performance NAS with 10 GbE** (for high-speed local network, VM hosting, heavy workloads)

These builds are **example configurations** (no external prices or URLs), focusing on *realistic parts*, *practicality*, and *homelab-friendly design*.

---

# 🔇 **Build 4 — Silent / Low-Power NAS (6-Disk RAIDZ-2)**

**Goal:** quiet, low-wattage, reliable, “invisible” NAS for the home.
Great for media (Plex/Jellyfin), backups, and general storage.

### 🧩 **Core Components**

**Case:**

* Fractal Design Node 804 (micro-ATX, very quiet, excellent airflow)

**Motherboard:**

* ASRock B550M Pro4 (micro-ATX, reliable, enough expansion options)

**CPU:**

* AMD Ryzen 5 5600G (low idle power, integrated graphics, perfect for NAS + light services)

**RAM:**

* 16 GB DDR4 (ECC if board supports it, otherwise standard)

**Drives:**

* 6 × NAS-grade 4 TB or 6 TB HDD

  * Lower-RPM (“5400 RPM class”) models strongly recommended for noise reduction

**HBA / SATA Expansion:**

* 8-port SATA PCIe card or LSI 9211-8i (IT mode)

**Boot Drive:**

* 120–250 GB SSD (for TrueNAS SCALE or similar)

**PSU:**

* 80+ Gold 400–500 W (Be Quiet! or Seasonic — extremely quiet)

### 🌡️ **Noise-Reduction Notes**

* Node 804 has soft-mount HDD trays reducing vibration
* Large low-RPM fans (120–140 mm)
* Ryzen 5600G idles at ~10–15 W → ideal for 24/7

**Best for:** quiet environments, low energy cost, long-term reliability.

---

# ⚡ **Build 5 — Performance NAS with 10 GbE (6-Disk RAIDZ-2)**

**Goal:** high throughput for video editing, VM storage, iSCSI, fast NFS/SMB.
Designed for ≥1 GB/s LAN speeds.

### 🧩 **Core Components**

**Case:**

* Fractal Design Define 7 or Define R5

  * Excellent airflow + noise insulation
  * Plenty of drive bays

**Motherboard:**

* Supermicro X12-series board (or equivalent workstation board)

  * Supports ECC
  * PCIe expansion lanes for HBAs + NICs
  * Server-grade reliability

**CPU:**

* Intel Xeon W-1290 or Core i5/i7 (10th/11th gen)

  * High IPC → great for ZFS, compression, containers, VMs

**RAM:**

* 32 GB DDR4 ECC (ZFS loves RAM — especially for high-throughput tasks)

**Drives:**

* 6 × 6 TB or 8 TB NAS-grade HDD
* Optional: 2 × NVMe SSDs for SLOG (sync writes) + L2ARC (read cache)

**HBA:**

* LSI 9300-8i or 9300-16i (enterprise-grade, IT mode)

**NIC:**

* 10 GbE PCIe card (Intel X550-T2 for RJ45, or Mellanox ConnectX-3/4 for SFP+)

**Boot Drive:**

* 250 GB SSD (OS)

**PSU:**

* 650 W 80+ Gold (Seasonic Focus or Corsair RMx)

### 🚀 **Performance Notes**

* With 10 GbE, RAIDZ-2 of 6 disks can push ~700–1000 MB/s sequential
* Add NVMe SLOG if using NFS/iSCSI for VMs (dramatically improves sync writes)
* Excellent for hypervisors (Proxmox, ESXi, etc.)

**Best for:** fast LAN storage, VM host backend, media editing, heavy homelab use.

---

# 📘 Summary of All 5 Builds

| Build # | Type                     | Capacity Range                | Noise        | Performance   | Ideal For                          |
| ------- | ------------------------ | ----------------------------- | ------------ | ------------- | ---------------------------------- |
| **1**   | Budget                   | ~8 TB usable                  | Medium       | Basic         | Backups, light NAS                 |
| **2**   | Balanced                 | ~16–17 TB usable              | Medium       | Good          | General homelab                    |
| **3**   | Future-Proof             | ~16–17 TB usable (expandable) | Medium       | High          | Lots of services, VMs              |
| **4**   | **Silent / Low-Power**   | ~12–30 TB usable              | **Very Low** | Moderate      | Living room, 24/7 quiet NAS        |
| **5**   | **Performance + 10 GbE** | ~16–50 TB usable              | Low-Medium   | **Very High** | VM storage, 10 GbE, high workloads |

---

# Want me to do one more thing?

I can also generate:

### ✔️ A **shopping list** for any of the builds

### ✔️ A **comparison** of ZFS vs Btrfs for your chosen build

### ✔️ A **step-by-step guide** for assembling and configuring your NAS (TrueNAS SCALE or Debian+ZFS)

### ✔️ A “best price-to-performance” recommendation tailored to **your budget**

**Which one would you like next?**

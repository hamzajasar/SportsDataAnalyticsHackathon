/**
 * All project copy in one place — edit text here, not in components.
 * Sections mirror the judging criteria (docs/JUDGING_CRITERIA.md).
 * Write for a coach / youth worker, not a data scientist.
 */

type ProjectContent = {
  name: string
  pitch: string
  problem: { who: string; decision: string }
  data: { label: string; value: string }[]
  method: { label: string; value: string }[]
  limitations: string[]
  impact: { label: string; value: string }[]
  team: { name: string; role: string }[]
}

const projectEn: ProjectContent = {
  name: 'Sustainable Sports Club',
  pitch:
    'We help community sports clubs in Bosnia and Herzegovina see where their carbon footprint comes from — electricity, away travel and kit — and pick the cheapest changes first, so that going green also makes sport cheaper and more accessible.',

  problem: {
    who: 'Community and youth sports clubs (volunteers, coaches, club boards)',
    decision:
      'How to travel to away games, how to cut energy use, and whether to buy new kit — with no time or budget to research the numbers',
  },

  data: [
    {
      label: 'Sources',
      value:
        'UK Government GHG Conversion Factors 2025 (OGL v3.0); Ember electricity data via Our World in Data (CC BY 4.0); Open-Meteo historical climate (CC BY 4.0); © OpenStreetMap contributors (ODbL); PVGIS solar yield (EC JRC)',
    },
    {
      label: 'Coverage',
      value:
        'Grid CO₂ intensity for 238 countries 1990–2025; 56 emission factors; Sarajevo monthly temperature and solar yield; BiH sports venues from OSM',
    },
    {
      label: 'Cleaning',
      value:
        'Reference tables committed to the repo; emission factors filtered to vehicle, material and grid categories; venue coordinates validated to the BiH bounding box (lat 42–46, lon 15–20)',
    },
  ],

  method: [
    {
      label: 'Approach',
      value:
        'Activity × official emission factor: kWh × grid intensity (Ember BiH), km × vehicle factor (UK GHG 2025), kg × material factor (UK GHG 2025)',
    },
    {
      label: 'Energy model',
      value:
        'Annual kWh split by use (floodlights, heating, hall); heating spread over months by heating degree days (base 15 °C, Open-Meteo temperatures); solar offset by PVGIS monthly yield × self-use share',
    },
    {
      label: 'Travel model',
      value:
        'Round-trip km × vehicles per trip × kg CO₂e per vehicle-km; hired coach per vehicle (35 assumed passengers); payback = upgrade cost ÷ yearly saving',
    },
    {
      label: 'Result',
      value:
        'A sample Sarajevo club could save ~4 000 KM/yr and cut 3+ t CO₂/yr — lowering the annual fee per child by ~80 KM — with LED lighting, modest solar and shared travel',
    },
  ],

  limitations: [
    'UK vehicle factors used as a proxy for BiH (older fleet → likely underestimates emissions)',
    'Kit weight, car occupancy and minibus size are configurable assumptions, not measured values',
    'Production (material) factors are averages, not brand-specific',
    'Solar yield uses Sarajevo PVGIS data — results vary by roof orientation and shading',
    'Affordability figure is a best case: assumes all upgrades are implemented simultaneously',
    'No real club data available at time of submission — all figures are illustrative',
  ],

  impact: [
    {
      label: 'Who benefits',
      value:
        'Youth and community clubs with tight budgets — the clubs where most children in BiH play sport',
    },
    {
      label: 'Inclusion',
      value:
        'Lower running costs → lower membership fees → more children can participate regardless of family income; tool works without technical knowledge',
    },
    {
      label: 'Adoption',
      value:
        'A club secretary can run the tool in 5 minutes on a phone; output is a one-page board report they can print and take to a municipal sport officer',
    },
  ],

  team: [{ name: 'Team 06', role: 'Data, Backend, Frontend' }],
}

const projectBs: ProjectContent = {
  name: 'Održivi sportski klub',
  pitch:
    'Pomažemo zajedničkim sportskim klubovima u Bosni i Hercegovini da sagledaju odakle dolazi njihov ugljični otisak — struja, gostovanja i oprema — i odaberu najjeftinije promjene prve, tako da zeleni pristup ujedno čini sport jeftinijim i dostupnijim.',

  problem: {
    who: 'Zajednički i omladinski sportski klubovi (volonteri, treneri, odbori kluba)',
    decision:
      'Kako putovati na gostovanja, kako smanjiti potrošnju energije i da li kupovati novu opremu — bez vremena ili budžeta za istraživanje podataka',
  },

  data: [
    {
      label: 'Izvori',
      value:
        'UK Government GHG Conversion Factors 2025 (OGL v3.0); Ember electricity data via Our World in Data (CC BY 4.0); Open-Meteo historical climate (CC BY 4.0); © OpenStreetMap contributors (ODbL); PVGIS solar yield (EC JRC)',
    },
    {
      label: 'Pokrivenost',
      value:
        'Intenzitet CO₂ mreže za 238 zemalja 1990–2025; 56 faktora emisija; Sarajevo — mjesečna temperatura i solarni prinos; Sportski objekti u BiH iz OSM',
    },
    {
      label: 'Čišćenje podataka',
      value:
        'Referentne tablice pohranjene u repozitoriju; faktori emisija filtrirani na kategorije vozila, materijala i mreže; koordinate objekata validirane na BiH okvir (lat 42–46, lon 15–20)',
    },
  ],

  method: [
    {
      label: 'Pristup',
      value:
        'Aktivnost × službeni faktor emisija: kWh × intenzitet mreže (Ember BiH), km × faktor vozila (UK GHG 2025), kg × faktor materijala (UK GHG 2025)',
    },
    {
      label: 'Model energije',
      value:
        'Godišnji kWh raspoređeni po namjeni (reflektori, grijanje, sala); grijanje raspoređeno po mjesecima prema stupanj-danima grijanja (baza 15 °C, temperature Open-Meteo); solarni odbitak po PVGIS mjesečnom prinosu × udio vlastite potrošnje',
    },
    {
      label: 'Model putovanja',
      value:
        'Povratni km × vozila po putovanju × kg CO₂e po vozilu-km; unajmljeni autobus po vozilu (35 pretpostavljenih putnika); povrat = trošak nadogradnje ÷ godišnja ušteda',
    },
    {
      label: 'Rezultat',
      value:
        'Primjerni sarajevski klub mogao bi uštedjeti ~4 000 KM/god i smanjiti 3+ t CO₂/god — snižavajući godišnju naknadu po djetetu za ~80 KM — LED rasvjetom, skromnim solarom i zajedničkim putovanjima',
    },
  ],

  limitations: [
    'Faktori za vozila iz UK koriste se kao aproksimacija za BiH (starija flota → vjerovatno podcjenjuje emisije)',
    'Težina opreme, popunjenost automobila i veličina minibusa su konfigurirane pretpostavke, a ne izmjerene vrijednosti',
    'Faktori proizvodnje (materijalni) su prosjeci, a ne specifični za brend',
    'Solarni prinos koristi Sarajevo PVGIS podatke — rezultati variraju ovisno o orijentaciji krova i sjeni',
    'Pristupačnost je optimistična procjena: pretpostavlja istovremenu provedbu svih nadogradnji',
    'Nije bilo dostupnih stvarnih podataka o klubu u trenutku predaje — sve cifre su ilustrativne',
  ],

  impact: [
    {
      label: 'Ko ima koristi',
      value:
        'Omladinski i zajednički klubovi s ograničenim budžetima — klubovi u kojima većina djece u BiH igra sport',
    },
    {
      label: 'Inkluzija',
      value:
        'Niži troškovi rada → niže članarine → više djece može sudjelovati bez obzira na prihode porodice; alat radi bez tehničkog znanja',
    },
    {
      label: 'Prihvatanje',
      value:
        'Sekretar kluba može koristiti alat za 5 minuta na telefonu; rezultat je jednostraničan izvještaj za odbor koji mogu odštampati i odnijeti općinskom sportskom savjetniku',
    },
  ],

  team: [{ name: 'Tim 06', role: 'Podaci, Backend, Frontend' }],
}

export const projectContent: Record<string, ProjectContent> = {
  en: projectEn,
  bs: projectBs,
}

export const project = projectEn

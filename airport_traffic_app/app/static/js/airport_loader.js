(function () {
  const airports = Object.freeze([
    { code: "ATL", name: "Atlanta (ATL) – Hartsfield-Jackson Atlanta International" },
    { code: "LAX", name: "Los Angeles (LAX) – Los Angeles International" },
    { code: "ORD", name: "Chicago (ORD) – O'Hare International" },
    { code: "DFW", name: "Dallas/Fort Worth (DFW) – Dallas/Fort Worth International" },
    { code: "DEN", name: "Denver (DEN) – Denver International" },
    { code: "JFK", name: "New York City (JFK) – John F. Kennedy International" },
    { code: "SFO", name: "San Francisco (SFO) – San Francisco International" },
    { code: "SEA", name: "Seattle (SEA) – Seattle-Tacoma International" },
    { code: "LAS", name: "Las Vegas (LAS) – Harry Reid International" },
    { code: "MCO", name: "Orlando (MCO) – Orlando International" },
    { code: "MIA", name: "Miami (MIA) – Miami International" },
    { code: "CLT", name: "Charlotte (CLT) – Charlotte Douglas International" },
    { code: "PHX", name: "Phoenix (PHX) – Sky Harbor International" },
    { code: "IAH", name: "Houston (IAH) – George Bush Intercontinental" },
    { code: "BOS", name: "Boston (BOS) – Logan International" }
  ]);

  window.MAJOR_US_AIRPORTS = airports;
  window.getMajorUsAirports = function () {
    return airports.slice();
  };
})();

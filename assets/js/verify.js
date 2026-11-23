/* Look up a CyberWithMadhav participation certificate ID against /assets/certificates.json. */
(function () {
  var form = document.getElementById("verify-form");
  var input = document.getElementById("certificate-id");
  var result = document.getElementById("verify-result");
  var LIST_URL = "/assets/certificates.json";

  function normalize(value) {
    return String(value || "").replace(/\s+/g, "").toUpperCase();
  }

  function setResult(state, title, bodyNode) {
    if (!result) return;
    result.hidden = false;
    result.className = "verify-result card " + state;
    result.replaceChildren();
    var heading = document.createElement("h2");
    heading.id = "verify-result-title";
    heading.textContent = title;
    result.appendChild(heading);
    if (bodyNode) result.appendChild(bodyNode);
  }

  function paragraph(text) {
    var p = document.createElement("p");
    p.className = "muted";
    p.textContent = text;
    return p;
  }

  function showMissing(id) {
    setResult(
      "is-missing",
      "Not found",
      paragraph(
        "No certificate with the ID " +
          id +
          " was found. Check the code on the certificate and try again. If you think this is a mistake, write to contact@cyberwithmadhav.com."
      )
    );
  }

  function showCert(cert) {
    var wrap = document.createElement("div");
    var fields = [
      ["Certificate ID", cert.id || cert.certificate_id],
      ["Name", cert.name],
      ["Institution", cert.institution],
      ["Session", cert.session],
      ["Date", cert.date]
    ];
    var dl = document.createElement("dl");
    dl.className = "verify-dl";
    fields.forEach(function (pair) {
      if (!pair[1]) return;
      var dt = document.createElement("dt");
      dt.textContent = pair[0];
      var dd = document.createElement("dd");
      dd.textContent = String(pair[1]);
      dl.appendChild(dt);
      dl.appendChild(dd);
    });
    wrap.appendChild(dl);
    var note = document.createElement("p");
    note.className = "small muted";
    note.textContent =
      "This is a participation record for a CyberWithMadhav awareness session. It is not a professional licence, an examination result, or a certification issued by any government department or examining body.";
    wrap.appendChild(note);
    setResult("is-found", "Certificate found", wrap);
  }

  function lookup(rawId) {
    var id = normalize(rawId);
    if (!id) {
      setResult("is-empty", "Enter an ID", paragraph("Enter a certificate ID, for example CWM-2026-XXXX."));
      return;
    }
    setResult("is-loading", "Checking", paragraph("Looking up this ID..."));
    fetch(LIST_URL, { cache: "no-store" })
      .then(function (res) {
        if (!res.ok) throw new Error("bad status");
        return res.json();
      })
      .then(function (data) {
        var list = (data && data.certificates) || [];
        var found = null;
        for (var i = 0; i < list.length; i += 1) {
          var item = list[i] || {};
          var itemId = normalize(item.id || item.certificate_id);
          if (itemId && itemId === id) {
            found = item;
            break;
          }
        }
        if (found) showCert(found);
        else showMissing(id);
        if (history.replaceState) {
          var url = new URL(window.location.href);
          url.searchParams.set("id", id);
          history.replaceState({}, "", url);
        }
      })
      .catch(function () {
        setResult(
          "is-error",
          "Could not check just now",
          paragraph(
            "The certificate list could not be loaded. Check your connection and try again, or write to contact@cyberwithmadhav.com."
          )
        );
      });
  }

  if (form) {
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      lookup(input ? input.value : "");
    });
  }

  var fromQuery = new URLSearchParams(window.location.search).get("id");
  if (fromQuery && input) {
    input.value = normalize(fromQuery);
    lookup(fromQuery);
  }
})();

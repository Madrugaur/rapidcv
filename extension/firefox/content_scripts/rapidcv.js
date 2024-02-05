(function () {
  function handle_generation(company, role) {
    function failure(err) {
      alert("Failure, see browser logs");
      if (err) console.error(err);
    }
    console.log(company, role);
    fetch(`http://localhost:64000/generate?company=${company}&role=${role}`, {
      method: "GET",
      mode: "cors",
    })
      .then((res) => {
        if (res.ok) {
          res
            .json()
            .then((j) => {
              alert(`Success: ${j.path}`);
            })
            .catch(failure);
        } else {
          failure(undefined);
        }
      })
      .catch(failure);
  }

  browser.runtime.onMessage.addListener((message) => {
    if (message.command === "generate") {
      handle_generation(message.company, message.role);
    }
  });
})();

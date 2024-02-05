function listenForClicks() {
  document.addEventListener("click", (e) => {
    function handle_generate_click(tabs) {
      function get_text_input(id) {
        const input = document.getElementById(id);
        if (!input) {
          console.error(`No element with id '${id}'`);
          return null;
        }
        if (input.value.length == 0) {
          return null;
        }
        return input.value;
      }

      const company = get_text_input("company_input");
      const role = get_text_input("role_input");
      if (!company || !role) {
        console.error(`Missing input; company: ${company}, role: ${role}`);
        return;
      }
      browser.tabs.sendMessage(tabs[0].id, {
        command: "generate",
        company: company,
        role: role,
      });
    }

    if (e.target.tagName !== "BUTTON" || !e.target.closest("#popup-content")) {
      return;
    }
    if (e.target.id != "generate_cv") {
      return;
    }
    browser.tabs
      .query({ active: true, currentWindow: true })
      .then(handle_generate_click)
      .catch(console.error);
  });
}

function handle_execution_error(err) {
  document.querySelector("#popup-content").classList.add("hidden");
  document.querySelector("#error-content").classList.remove("hidden");
  console.error(err);
}

browser.tabs
  .executeScript({ file: "/content_scripts/rapidcv.js" })
  .then(listenForClicks)
  .catch(handle_execution_error);

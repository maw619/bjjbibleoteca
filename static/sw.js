self.addEventListener("push", (event) => {
  let data = { title: "BJJ Biblioteca", body: "New activity" };
  try {
    if (event.data) data = event.data.json();
  } catch (e) {}

  event.waitUntil(
    self.registration.showNotification(data.title || "BJJ Biblioteca", {
      body: data.body || "New activity",
    })
  );
});

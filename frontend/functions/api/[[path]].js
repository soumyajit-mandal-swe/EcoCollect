export async function onRequest({ request }) {
  const url = new URL(request.url);

  url.protocol = "https:";
  url.hostname = "ecocollect-api-zrqm.onrender.com";
  url.port = "";

  return fetch(new Request(url.toString(), request));
}
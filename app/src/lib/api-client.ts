import createFetchClient from "openapi-fetch";
import createClient from "openapi-react-query";
import type { paths } from "../types/api";
console.log("EXPO_API_BASE_URL:", process.env.EXPO_API_BASE_URL);

const fetchClient = createFetchClient<paths>({
  baseUrl: process.env.EXPO_API_BASE_URL || "http://localhost:8000",
});
const $api = createClient(fetchClient);

export default $api;

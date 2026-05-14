import createClient from "openapi-fetch";
import type { paths } from "./types";

export const apiClient = createClient<paths>({
  baseUrl: import.meta.env.API_BASE_URL || "http://localhost:8000",
});

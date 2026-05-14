import { useQuery } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

export function useRecipe(recipeId: string) {
  return useQuery({
    queryKey: ["recipe", recipeId],
    queryFn: async () => {
      const response = await apiClient.GET("/api/v1/recipes/{recipe_id}", {
        params: { path: { recipe_id: recipeId } },
      });
      if (response.error) throw new Error("Failed to fetch recipe");
      return response.data;
    },
  });
}

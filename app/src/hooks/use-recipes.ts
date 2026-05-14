import { useInfiniteQuery } from "@tanstack/react-query";
import { apiClient } from "@/api/client";

interface UseRecipesOptions {
  pageSize?: number;
}

export const useRecipes = (options: UseRecipesOptions = {}) => {
  const { pageSize = 10 } = options;

  return useInfiniteQuery({
    queryKey: ["recipes", pageSize],
    queryFn: async ({ pageParam }) => {
      const { data, error } = await apiClient.GET("/api/v1/recipes", {
        params: {
          query: {
            page: pageParam as number,
            page_size: pageSize,
          },
        },
      });

      if (error) {
        throw new Error("Failed to fetch recipes");
      }

      return data;
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => {
      if (lastPage.page < lastPage.total_pages) {
        return lastPage.page + 1;
      }
      return undefined;
    },
  });
};

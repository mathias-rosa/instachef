import $api from "./api-client";

export function useRecipes() {
  return $api.useInfiniteQuery(
    "get",
    "/api/v1/recipes",
    {},
    {
      getNextPageParam: (lastPage) => {
        if (lastPage.page < lastPage.total_pages) {
          return lastPage.page + 1;
        }
        return undefined;
      },
      initialPageParam: 0,
    },
  );
}

export function useRecipe(id: string) {
  return $api.useQuery("get", "/api/v1/recipes/{recipe_id}", {
    params: {
      path: { recipe_id: id },
    },
  });
}

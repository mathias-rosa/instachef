import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/recipe/$id")({
  component: RecipePage,
});

function RecipePage() {
  const { id } = Route.useParams();

  return <div>Recette {id}</div>;
}

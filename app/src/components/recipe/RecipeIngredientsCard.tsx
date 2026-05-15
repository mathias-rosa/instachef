import { Card, Typography } from "@heroui/react";
import type { components } from "@/api/types";

type Ingredient = components["schemas"]["Ingredient"];

type RecipeIngredientsCardProps = {
  ingredients: Ingredient[];
};

const formatIngredient = (ingredient: Ingredient) => {
  const parts: Array<string | number> = [];

  if (ingredient.quantity != null) {
    parts.push(ingredient.quantity);
  }

  if (ingredient.unit) {
    parts.push(ingredient.unit);
  }

  if (parts.length === 0 && ingredient.count != null) {
    parts.push(ingredient.count);
  }

  parts.push(ingredient.name);
  return parts.join(" ");
};

export const RecipeIngredientsCard = ({
  ingredients,
}: RecipeIngredientsCardProps) => {
  const ingredientGroups = ingredients.reduce(
    (acc, ingredient) => {
      const group = ingredient.group || "Autres";
      if (!acc[group]) acc[group] = [];
      acc[group].push(ingredient);
      return acc;
    },
    {} as Record<string, Ingredient[]>,
  );

  return (
    <Card className="gap-4">
      <Card.Header>
        <Typography.Heading level={4}>Ingredients</Typography.Heading>
      </Card.Header>
      <Card.Content className="space-y-4">
        {Object.entries(ingredientGroups).map(([group, groupIngredients]) => (
          <div key={group} className="space-y-2">
            <p className="text-sm font-semibold text-accent">{group}</p>
            <ul className="space-y-2 text-sm">
              {groupIngredients.map((ingredient, index) => (
                <li key={`${group}-${index}`} className="flex gap-2">
                  <span className="text-muted">•</span>
                  <span>
                    {formatIngredient(ingredient)}
                    {ingredient.note ? (
                      <span className="ml-1 text-xs text-muted">
                        ({ingredient.note})
                      </span>
                    ) : null}
                  </span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </Card.Content>
    </Card>
  );
};

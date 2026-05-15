import { cn } from "@heroui/react";
import type { components } from "@/api/types";
import { RecipeBackLink } from "@/components/recipe/RecipeBackLink";
import { RecipeIngredientsCard } from "@/components/recipe/RecipeIngredientsCard";
import { RecipeInstructionsCard } from "@/components/recipe/RecipeInstructionsCard";
import { RecipeSummaryCard } from "@/components/recipe/RecipeSummaryCard";
import { RecipeTagsCard } from "@/components/recipe/RecipeTagsCard";
import { RecipeTipsCard } from "@/components/recipe/RecipeTipsCard";

type RecipeRecord = components["schemas"]["RecipeRecord"];
type RecipeDetailProps = {
  record: RecipeRecord;
  className?: string;
};

export const RecipeDetail = ({ record, className }: RecipeDetailProps) => {
  const { recipe, source } = record;

  const reelUrl = source.source_type === "reel" ? source.reel_url : null;

  return (
    <div className={cn("space-y-6", className)}>
      <RecipeBackLink />
      <RecipeSummaryCard recipe={recipe} reelUrl={reelUrl} />

      <div className="grid gap-6 md:grid-cols-2">
        <RecipeIngredientsCard ingredients={recipe.ingredients} />
        <RecipeInstructionsCard instructions={recipe.instructions} />
      </div>
      <RecipeTipsCard tips={recipe.tips} />
      <RecipeTagsCard tags={recipe.tags} />
    </div>
  );
};

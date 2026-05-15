import { Button, Card, cn, Separator } from "@heroui/react";
import { ChefHat, Clock, Flame, Tag, Timer, Users } from "lucide-react";
import { Instagram } from "../icons/instagram";
import { MetadataCard } from "../MetadataCard";
import type { components } from "@/api/types";

type Recipe = components["schemas"]["Recipe"];

type RecipeSummaryCardProps = {
  recipe: Recipe;
  reelUrl?: string | null;
};

export const RecipeSummaryCard = ({
  recipe,
  reelUrl,
}: RecipeSummaryCardProps) => (
  <Card className="gap-4">
    <Card.Header className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
      <div className="space-y-2">
        <Card.Title className="text-2xl md:text-3xl font-display py-2">
          {recipe.title}
        </Card.Title>
        <Card.Description className="text-base text-muted">
          {recipe.description}
        </Card.Description>
      </div>

      {reelUrl ? (
        <Button
          className="gap-2"
          onPress={() => {
            window.open(reelUrl, "_blank", "noopener,noreferrer");
          }}
        >
          <Instagram size={16} />
          Voir le reel
        </Button>
      ) : null}
    </Card.Header>

    <Card.Content className="space-y-4">
      <div
        className={cn(
          recipe.servings ? "sm:grid-cols-4" : "grid-cols-2 sm:grid-cols-3",
          "grid-cols-2 grid gap-3",
        )}
      >
        <MetadataCard>
          <MetadataCard.Icon>
            <ChefHat />
          </MetadataCard.Icon>
          <MetadataCard.Content>
            <MetadataCard.Label>Cuisine</MetadataCard.Label>
            <MetadataCard.Value>{recipe.cuisine_type}</MetadataCard.Value>
          </MetadataCard.Content>
        </MetadataCard>
        <MetadataCard>
          <MetadataCard.Icon>
            <Tag />
          </MetadataCard.Icon>
          <MetadataCard.Content>
            <MetadataCard.Label>Type</MetadataCard.Label>
            <MetadataCard.Value>{recipe.dish_type}</MetadataCard.Value>
          </MetadataCard.Content>
        </MetadataCard>
        <MetadataCard>
          <MetadataCard.Icon>
            <Flame />
          </MetadataCard.Icon>
          <MetadataCard.Content>
            <MetadataCard.Label>Difficulté</MetadataCard.Label>
            <MetadataCard.Value>{recipe.difficulty}</MetadataCard.Value>
          </MetadataCard.Content>
        </MetadataCard>
        {recipe.servings ? (
          <MetadataCard>
            <MetadataCard.Icon>
              <Users />
            </MetadataCard.Icon>
            <MetadataCard.Content>
              <MetadataCard.Label>Portions</MetadataCard.Label>
              <MetadataCard.Value>{recipe.servings}</MetadataCard.Value>
            </MetadataCard.Content>
          </MetadataCard>
        ) : null}
      </div>

      <Separator />

      <div className="grid gap-3 grid-cols-3">
        <Card variant="secondary" className="p-3 text-center shadow-none">
          <Card.Content className="space-y-1">
            <Clock size={18} className="mx-auto text-accent" />
            <p className="text-xs text-muted">Preparation</p>
            <p className="text-sm font-medium">
              {recipe.prep_time_minutes ?? 0} min
            </p>
          </Card.Content>
        </Card>
        <Card variant="secondary" className="p-3 text-center shadow-none">
          <Card.Content className="space-y-1">
            <Flame size={18} className="mx-auto text-accent" />
            <p className="text-xs text-muted">Cuisson</p>
            <p className="text-sm font-medium">
              {recipe.cook_time_minutes ?? 0} min
            </p>
          </Card.Content>
        </Card>
        <Card variant="secondary" className="p-3 text-center shadow-none">
          <Card.Content className="space-y-1">
            <Timer size={18} className="mx-auto text-accent" />
            <p className="text-xs text-muted">Repos</p>
            <p className="text-sm font-medium">
              {recipe.rest_time_minutes ?? 0} min
            </p>
          </Card.Content>
        </Card>
      </div>
    </Card.Content>
  </Card>
);

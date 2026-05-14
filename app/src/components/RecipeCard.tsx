import { Card, Chip, cn } from "@heroui/react";
import { Link } from "@tanstack/react-router";
import { Clock, Users } from "lucide-react";
import type { components } from "@/api/types";

type RecipeRecord = components["schemas"]["RecipeRecord"];

type RecipeCardProps = {
  record: RecipeRecord;
  className?: string;
};

export const RecipeCard = ({ record, className }: RecipeCardProps) => {
  const { recipe, source } = record;
  const totalMinutes =
    (recipe.prep_time_minutes ?? 0) + (recipe.cook_time_minutes ?? 0);
  const hasTime = totalMinutes > 0;

  const defaultClassName = "h-full flex-1";

  return (
    <Link to="/recipe/$id" params={{ id: record.id }}>
      <Card className={cn(defaultClassName, className)}>
        <Card.Header className="flex flex-col gap-2">
          <Card.Title className="text-lg">{recipe.title}</Card.Title>
          <Card.Description className="line-clamp-2">
            {recipe.description}
          </Card.Description>
        </Card.Header>

        <Card.Content className="space-y-3">
          <div className="flex flex-wrap gap-2">
            <Chip size="sm">{recipe.cuisine_type}</Chip>
            <Chip size="sm">{recipe.dish_type}</Chip>
          </div>
        </Card.Content>

        <Card.Footer className="text-xs opacity-70">
          <div className="flex flex-wrap gap-4">
            {hasTime ? (
              <span className="flex items-center gap-1">
                <Clock size={14} />
                {totalMinutes} min
              </span>
            ) : null}
            {recipe.servings ? (
              <span className="flex items-center gap-1">
                <Users size={14} />
                {recipe.servings}
              </span>
            ) : null}
            {source.source_type === "reel" && source.author ? (
              <span>{source.author}</span>
            ) : null}
          </div>
        </Card.Footer>
      </Card>
    </Link>
  );
};

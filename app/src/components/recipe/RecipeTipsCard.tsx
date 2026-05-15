import { Card, Typography } from "@heroui/react";
import { Lightbulb } from "lucide-react";

type RecipeTipsCardProps = {
  tips?: string[];
};

export const RecipeTipsCard = ({ tips }: RecipeTipsCardProps) => {
  if (!tips || tips.length === 0) {
    return null;
  }

  return (
    <Card className="gap-3">
      <Card.Header>
        <Typography.Heading level={4}>Conseils</Typography.Heading>
      </Card.Header>
      <Card.Content>
        <ul className="space-y-2">
          {tips.map((tip, index) => (
            <li key={`tip-${index}`} className="flex gap-2 text-sm">
              <Lightbulb size={16} className="text-accent" />
              <span className="text-muted">{tip}</span>
            </li>
          ))}
        </ul>
      </Card.Content>
    </Card>
  );
};

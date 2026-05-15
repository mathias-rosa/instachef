import { Card, Chip, Typography } from "@heroui/react";
import { Tag } from "lucide-react";

type RecipeTagsCardProps = {
  tags?: string[];
};

export const RecipeTagsCard = ({ tags }: RecipeTagsCardProps) => {
  if (!tags || tags.length === 0) {
    return null;
  }

  return (
    <Card className="gap-3">
      <Card.Header>
        <Typography.Heading level={4}>Tags</Typography.Heading>
      </Card.Header>
      <Card.Content className="flex flex-wrap gap-2">
        {tags.map((tag, index) => (
          <Chip key={`${tag}-${index}`} size="sm" className="gap-2">
            <Tag size={12} />
            {tag}
          </Chip>
        ))}
      </Card.Content>
    </Card>
  );
};

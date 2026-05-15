import { Card, Typography } from "@heroui/react";
import type { components } from "@/api/types";

type InstructionStep = components["schemas"]["InstructionStep"];

type RecipeInstructionsCardProps = {
  instructions: InstructionStep[];
};

export const RecipeInstructionsCard = ({
  instructions,
}: RecipeInstructionsCardProps) => (
  <Card className="gap-4">
    <Card.Header>
      <Card.Header>
        <Typography.Heading level={4}>Instructions</Typography.Heading>
      </Card.Header>
    </Card.Header>
    <Card.Content>
      <ol className="space-y-4">
        {instructions.map((instruction, index) => (
          <li key={`instruction-${index}`} className="flex gap-3">
            <span className="shrink-0 w-7 h-7 sm:w-8 sm:h-8 flex items-center justify-center bg-accent text-accent-foreground rounded-full ">
              {index + 1}
            </span>
            <div>
              {instruction.title ? (
                <p className="text-sm font-semibold">{instruction.title}</p>
              ) : null}
              <p className="text-sm text-muted">{instruction.description}</p>
            </div>
          </li>
        ))}
      </ol>
    </Card.Content>
  </Card>
);

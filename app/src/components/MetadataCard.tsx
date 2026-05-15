import { cn, Surface, type SurfaceVariants } from "@heroui/react";
import type { ReactNode } from "react";

type MetadataCardRootProps = {
  children: ReactNode;
  className?: string;
  variant?: SurfaceVariants["variant"];
};

type MetadataCardIconProps = {
  children: ReactNode;
};

type MetadataCardLabelProps = {
  children: string;
};

type MetadataCardValueProps = {
  children: string | number;
};

const MetadataCardRoot = ({
  children,
  variant = "tertiary",
  className,
}: MetadataCardRootProps) => (
  <Surface
    variant={variant}
    className={cn(
      "flex flex-row items-center rounded-2xl gap-3 px-3 py-2",
      className,
    )}
  >
    {children}
  </Surface>
);

const MetadataCardIcon = ({ children }: MetadataCardIconProps) => (
  <div className="text-muted shrink-0">{children}</div>
);

const MetadataCardContent = ({ children }: { children: ReactNode }) => (
  <div className="min-w-0">{children}</div>
);

const MetadataCardLabel = ({ children }: MetadataCardLabelProps) => (
  <p className="text-xs text-muted">{children}</p>
);

const MetadataCardValue = ({ children }: MetadataCardValueProps) => (
  <p className="truncate text-sm font-medium">{children}</p>
);

const MetadataCard = Object.assign(MetadataCardRoot, {
  Icon: MetadataCardIcon,
  Content: MetadataCardContent,
  Label: MetadataCardLabel,
  Value: MetadataCardValue,
});

export { MetadataCard };

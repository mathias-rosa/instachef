import { Link } from "@tanstack/react-router";
import { ArrowLeft } from "lucide-react";

export const RecipeBackLink = () => (
  <Link
    to="/recipes"
    className="link inline-flex items-center gap-2 text-sm text-muted hover:text-foreground"
  >
    <ArrowLeft size={16} />
    Retour aux recettes
  </Link>
);

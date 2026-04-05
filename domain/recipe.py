from enum import StrEnum
from pydantic import BaseModel, Field


class CuisineType(StrEnum):
    FRANCAISE = "française"
    ITALIENNE = "italienne"
    ASIATIQUE = "asiatique"
    MOYEN_ORIENTALE = "moyen-orientale"
    AMERICAINE = "américaine"
    MEDITERRANEENNE = "méditerranéenne"
    MEXICAINE = "mexicaine"
    INDIENNE = "indienne"
    AUTRE = "autre"


class DishType(StrEnum):
    ENTREE = "entrée"
    PLAT = "plat principal"
    DESSERT = "dessert"
    SNACK = "snack"
    BOISSON = "boisson"
    SAUCE = "sauce"


class Difficulty(StrEnum):
    FACILE = "facile"
    MOYEN = "moyen"
    DIFFICILE = "difficile"


class Appliance(StrEnum):
    FOUR = "four"
    AIRFRYER = "airfryer"
    MICRO_ONDES = "micro-ondes"
    MIXEUR = "mixeur"
    ROBOT_CULINAIRE = "robot culinaire"
    BATTEUR = "batteur électrique"
    CUISEUR_VAPEUR = "cuiseur vapeur"
    PLAQUE = "plaque de cuisson"
    AUTRE = "autre"


class Ingredient(BaseModel):
    name: str = Field(
        description="Nom de l'ingrédient uniquement. Ex: 'poulet', 'ail'."
    )
    quantity: float | None = Field(
        None,
        description="Valeur numérique uniquement. Ex: 2.0, 0.5, 680.0. None si non mesurable.",
    )
    unit: str | None = Field(
        None,
        description="Unité de mesure. Ex: 'g', 'ml', 'c.à.s.', 'c.à.c.'. None si compté en unités.",
    )
    count: int | None = Field(
        None,
        description="Nombre d'unités entières. Ex: 3 œufs, 2 citrons. None si quantity/unit renseignés.",
    )
    note: str | None = Field(
        None,
        description="Préparation ou précision. Ex: 'finement haché', 'à température ambiante'.",
    )
    group: str | None = Field(
        None,
        description="Groupe d'appartenance si la recette a des composants distincts. Ex: 'Marinade', 'Sauce', 'Garniture'. None si recette plate.",
    )


class InstructionStep(BaseModel):
    title: str | None = Field(
        None,
        description="Titre court de l'étape. Ex: 'Marinade', 'Cuisson du riz', 'Dressage'. None si l'étape ne correspond pas à une phase distincte.",
    )
    description: str = Field(description="Instructions détaillées de l'étape.")


class Recipe(BaseModel):
    title: str
    description: str = Field(
        description="Une phrase qui donne envie et résume le plat."
    )
    cuisine_type: CuisineType
    dish_type: DishType
    difficulty: Difficulty

    prep_time_minutes: int | None = Field(
        None, description="Temps de préparation actif en minutes."
    )
    cook_time_minutes: int | None = Field(
        None, description="Temps de cuisson en minutes."
    )
    rest_time_minutes: int | None = Field(
        None, description="Marinade, repos, réfrigération. None si absent."
    )

    servings: int | None = Field(
        None, description="Nombre de personnes. None si non déductible."
    )

    appliances: list[Appliance] = Field(
        default_factory=list,
        description="Appareils électroménagers requis. Vide si cuisson standard.",
    )
    utensils: list[str] = Field(
        default_factory=list,
        description="Ustensiles notables. Ex: 'wok', 'mandoline'. Exclure couteau, planche, bol.",
    )

    ingredients: list[Ingredient]
    instructions: list[InstructionStep]

    tags: list[str] = Field(
        default_factory=list,
        description="Mots-clés courts. Ex: 'one-pan', 'meal-prep', 'sans gluten'.",
    )
    tips: list[str] = Field(
        default_factory=list,
        description="Astuces du créateur visibles dans la vidéo ou la caption.",
    )

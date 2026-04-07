import { useEffect, useMemo, useState } from 'react'
import { Button, Card, Chip, Spinner } from '@heroui/react'
import { supabase } from './lib/supabase'

type RecipeData = {
  title?: string
  description?: string
  dish_type?: string
  difficulty?: string
  total_time_minutes?: number
  servings?: number
  ingredients?: Array<string | Record<string, unknown>>
  instructions?: string[]
  tags?: string[]
}

type SourceData = {
  author?: string
  reel_url?: string
}

type RecipeRecord = {
  id: string
  recipe: RecipeData
  source: SourceData
  created_at: string | null
}

function formatDate(iso: string | null): string {
  if (!iso) {
    return 'Date inconnue'
  }

  return new Intl.DateTimeFormat('fr-FR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(iso))
}

function ingredientToLabel(ingredient: string | Record<string, unknown>): string {
  if (typeof ingredient === 'string') {
    return ingredient
  }

  const quantity = ingredient.quantity
  const unit = ingredient.unit
  const name = ingredient.name
  const note = ingredient.note

  const parts = [quantity, unit, name]
    .filter((part) => typeof part === 'string' || typeof part === 'number')
    .map((part) => String(part).trim())
    .filter(Boolean)

  let label = parts.join(' ')

  if (typeof note === 'string' && note.trim()) {
    label = label ? `${label} (${note.trim()})` : note.trim()
  }

  if (!label) {
    return 'Ingrédient sans détail'
  }

  return label
}

function App() {
  const [records, setRecords] = useState<RecipeRecord[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [query, setQuery] = useState('')

  async function loadRecipes() {
    setIsLoading(true)
    setError(null)

    const { data, error: supabaseError } = await supabase
      .from('recipes')
      .select('id, recipe, source, created_at')
      .order('created_at', { ascending: false })
      .limit(100)

    if (supabaseError) {
      setError(supabaseError.message)
      setIsLoading(false)
      return
    }

    setRecords((data as RecipeRecord[]) ?? [])
    setIsLoading(false)
  }

  useEffect(() => {
    loadRecipes()
  }, [])

  const filteredRecords = useMemo(() => {
    const normalized = query.trim().toLowerCase()
    if (!normalized) {
      return records
    }

    return records.filter((record) => {
      const title = record.recipe?.title ?? ''
      const author = record.source?.author ?? ''
      const id = record.id
      return [title, author, id].some((value) =>
        value.toLowerCase().includes(normalized),
      )
    })
  }, [records, query])

  return (
    <main className="page-shell">
      <section className="page-header">
        <div>
          <p className="kicker">InstaCHEF Dashboard</p>
          <h1>Recettes extraites depuis Supabase</h1>
          <p className="subtitle">
            Explore les reels déjà traités, vérifie rapidement les ingrédients,
            puis ouvre la source Instagram si besoin.
          </p>
        </div>
        <div className="toolbar">
          <input
            type="search"
            className="search"
            placeholder="Filtrer par titre, auteur ou ID"
            value={query}
            onChange={(event) => setQuery(event.target.value)}
          />
          <Button variant="primary" onPress={loadRecipes}>
            Rafraîchir
          </Button>
        </div>
      </section>

      {isLoading ? (
        <section className="state-card" aria-live="polite">
          <div className="loading-state">
            <Spinner aria-label="Chargement des recettes" />
            <p>Chargement des recettes...</p>
          </div>
        </section>
      ) : null}

      {!isLoading && error ? (
        <section className="state-card error" aria-live="assertive">
          <p>Erreur Supabase: {error}</p>
          <Button variant="secondary" onPress={loadRecipes}>
            Réessayer
          </Button>
        </section>
      ) : null}

      {!isLoading && !error ? (
        <section className="recipes-grid">
          {filteredRecords.map((record) => (
            <Card key={record.id} variant="secondary" className="recipe-card">
              <Card.Header>
                <Card.Title>
                  {record.recipe?.title?.trim() || 'Recette sans titre'}
                </Card.Title>
                <Card.Description>
                  {record.source?.author
                    ? `@${record.source.author}`
                    : 'Auteur inconnu'}
                </Card.Description>
              </Card.Header>

              <Card.Content>
                <p className="meta">{formatDate(record.created_at)}</p>
                <p className="description">
                  {record.recipe?.description?.trim() ||
                    'Aucune description fournie.'}
                </p>

                <div className="chip-row">
                  {record.recipe?.dish_type ? (
                    <Chip variant="soft">{record.recipe.dish_type}</Chip>
                  ) : null}
                  {record.recipe?.difficulty ? (
                    <Chip variant="soft">{record.recipe.difficulty}</Chip>
                  ) : null}
                  {record.recipe?.servings ? (
                    <Chip variant="soft">
                      {record.recipe.servings} portions
                    </Chip>
                  ) : null}
                </div>

                <div className="ingredients-preview">
                  {(record.recipe?.ingredients ?? [])
                    .slice(0, 5)
                    .map((ingredient, index) => {
                      const label = ingredientToLabel(ingredient)
                      return <p key={`${record.id}-${index}`}>• {label}</p>
                    })}
                </div>
              </Card.Content>

              <Card.Footer>
                <span className="record-id">{record.id}</span>
                {record.source?.reel_url ? (
                  <a
                    href={record.source.reel_url}
                    target="_blank"
                    rel="noreferrer"
                    className="link-button"
                  >
                    Ouvrir le reel
                  </a>
                ) : null}
              </Card.Footer>
            </Card>
          ))}
        </section>
      ) : null}
    </main>
  )
}

export default App

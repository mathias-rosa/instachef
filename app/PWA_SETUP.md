# InstaChef PWA Setup

## Configuration PWA

L'app utilise `vite-plugin-pwa` pour le support Progressive Web App.

### Fonctionnalités activées

- ✅ **Service Worker** - Caching automatique et offline support
- ✅ **Installable** - Bouton "Installer" sur mobile & desktop
- ✅ **Auto-update** - Mise à jour automatique en arrière-plan
- ✅ **Web App Manifest** - Métadonnées pour les stores

### Fichiers générés

- `dist/sw.js` - Service Worker (auto-généré)
- `dist/workbox-*.js` - Runtime caching (auto-généré)
- `public/manifest.json` - Web App Manifest

### Icônes requises

Remplace ces fichiers PNG dans `public/`:

- `icon-192.png` - 192x192 (app launcher)
- `icon-512.png` - 512x512 (splash screen)
- `icon-192-maskable.png` - 192x192 (maskable icon)
- `icon-512-maskable.png` - 512x512 (maskable icon)

Utilise des icônes carrées (pas de transparence pour maskable).

### Testing PWA

```bash
# Build
bun run build

# Serve dist/ avec HTTPS (pwа requiert https en prod)
# ou localhost fonctionne en dev
npx serve dist
```

Puis ouvre DevTools → Application → Manifest pour vérifier l'installation.

### Caching API

Configuré dans `vite.config.ts`:

- Assets statiques: caching illimité
- API calls: 24h de cache avec fallback offline
- Max file size: 5MB

### HTTPS requis en production

PWA nécessite HTTPS pour la sécurité. En dev, localhost est autorisé.

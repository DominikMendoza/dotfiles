# worktree

Documentación para humanos de la skill `/worktree`. El `SKILL.md` que está al
lado es lo que Claude lee y ejecuta. Este archivo explica qué hace y por qué.

English version: [README.md](README.md)

## El problema que resuelve

Cambiar de rama con `git checkout` tumba todo lo que estaba caliente. El dev
server se detiene, el build incremental se descarta, y si las ramas declaran
dependencias distintas hay que reinstalar.

Ese costo da igual una vez al día. No da igual cuando hay dos cards pequeñas en
vuelo y la idea es justamente que una siga corriendo mientras la otra avanza.

Un worktree es un segundo directorio de trabajo sobre el mismo `.git`. Dos
checkouts, dos índices, un solo repositorio. No se duplica nada ni se vuelve a
traer nada de la red.

## Estructura de directorios

El worktree es hermano del repositorio y lleva el nombre de su rama.

```
~/Projects/
  services/                              <- carpeta principal
  HAT-990-expand-reconnect-tooltip/      <- worktree
  HAT-985-fix-order-total/               <- otro worktree
```

## Qué pasa al crear uno

```
                     git fetch origin <base>
                              |
               git ls-remote --heads origin <rama>
                              |
         +--------------------+--------------------+
         |                                         |
   existe en origin                         no existe
         |                                         |
  se crea desde origin/<rama>           se crea desde origin/<base>
  los nombres coinciden, se enlaza      con --no-track, sin upstream
         |                                         |
         +--------------------+--------------------+
                              |
                    hay package.json?
                              |
              comparar lockfile contra principal
                              |
              identico  -> symlink de node_modules
              distinto  -> npm ci
```

La base es `develop`, `staging` o `master-hotfix`, y por defecto `staging`.

Los cambios sin commitear en la carpeta principal no bloquean nada de esto.
`git worktree add` nunca toca ese directorio.

Si la rama ya está tomada por otro worktree, git se niega. La skill reporta en
qué ruta está y para, en lugar de forzar.

## node_modules, y por qué un symlink en vez de pnpm

Cada worktree necesita su propio `node_modules`, y un install completo por card
es lento y pesado.

pnpm resuelve esto de raíz, porque su store direccionado por contenido convierte
cada install en un conjunto de hardlinks. Se evaluó y se pospuso a propósito. Su
`node_modules` no es plano, así que cualquier paquete que importe algo que no
declara deja de resolver, cosa común en frontends con años encima. Es un riesgo
real a cambio de un beneficio que no hace falta mientras solo corra un dev server
a la vez.

Entonces la skill compara el lockfile contra la carpeta principal. Si son
idénticos las dependencias también lo son, y hace un symlink al `node_modules`
que ya existe. Es instantáneo, no ocupa disco, y es seguro porque nadie más lo
está usando. Si el lockfile difiere, la rama cambió sus dependencias y le toca un
`npm ci` real.

Si algún día hacen falta dos dev servers simultáneos, el siguiente paso es pnpm
con `node-linker=hoisted`.

## La trampa del slash final

Los `.gitignore` de los repos suelen decir `node_modules/`, con slash final, que
solo matchea directorios. El symlink que creamos no es un directorio, así que el
patrón no lo cubre. Aparece como archivo sin trackear, y entonces
`git worktree remove` se niega a borrar el worktree:

```
fatal: '../HAT-990-...' contains modified or untracked files, use --force to delete it
```

El arreglo es `node_modules`, sin slash final, en el exclude local:

```
EXCLUDE="$(git rev-parse --git-common-dir)/info/exclude"
grep -qx node_modules "$EXCLUDE" || echo node_modules >> "$EXCLUDE"
```

`.git/info/exclude` es por clon y nunca se pushea, así que ni el repositorio ni
el resto del equipo ven nada. Se escribe una sola vez y aplica a todos los
worktrees, porque `info/` vive en el git compartido. La skill lo hace sola la
primera vez que corre.

## Cómo recuperar el trabajo en la carpeta principal

No hay nada que mover. El worktree comparte el mismo `.git`, así que cada commit
hecho adentro ya es visible desde la carpeta principal en el instante en que
existe. No hace falta pushear, ni cherry-pick, ni copiar archivos.

El único obstáculo es que git mantiene una rama en un solo worktree a la vez. Al
quitar el worktree la rama queda libre:

```
git worktree remove ../HAT-990-expand-reconnect-tooltip
git checkout HAT-990-expand-reconnect-tooltip
```

Para trabajo sin commitear, el stash se comparte entre worktrees: `git stash`
dentro del worktree y `git stash pop` desde la carpeta principal.

## Al terminar la card

```
git worktree list
git worktree remove ../HAT-990-expand-reconnect-tooltip
git worktree prune
```

`remove` se niega cuando el directorio tiene archivos modificados o sin trackear.
Esa protección se quiere, así que la skill reporta qué está sucio y espera en vez
de forzar. El borrado no sigue el symlink de `node_modules`, de modo que la
carpeta principal conserva el suyo.

`prune` limpia los registros de worktrees cuyo directorio se borró a mano.

## De qué depende

| Pieza | Para qué |
| ----- | -------- |
| `branch.autoSetupMerge = simple` | Una rama nueva desde `origin/staging` nace sin upstream, y una rama cuyo nombre coincide con el remoto queda enlazada sola. Los dos comportamientos con un solo ajuste. |
| Acceso de red a Bitbucket | Lo resuelve el alias `bb`. Ver el README de la raiz del repositorio. |
| `~/.claude/CLAUDE.md` | Aporta las reglas de nombre de rama: `<KEY>-<descripcion>`, 40 caracteres máximo. |

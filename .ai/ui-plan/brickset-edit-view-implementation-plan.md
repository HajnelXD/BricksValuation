# Plan implementacji widoku edycji i usuwania zestawu BrickSet

## 1. Przegląd
Widok edycji zestawu (`BrickSetEditView`) umożliwia właścicielowi modyfikację danych zestawu oraz jego usunięcie, pod warunkiem spełnienia reguł biznesowych (RB-01): zestaw nie może mieć wyceny od innego użytkownika oraz wycena właściciela (jeśli istnieje) nie może mieć żadnych lajków. Widok zapewnia przejrzystą komunikację o możliwości edycji/usunięcia oraz obsługuje wszystkie przypadki błędów z odpowiednimi komunikatami dla użytkownika.

## 2. Routing widoku
- **Ścieżka edycji**: `/app/bricksets/:id/edit`
- **Parametr**: `:id` - identyfikator zestawu (number)
- **Guard**: `requireAuth` - wymaga zalogowania
- **Meta**: `{ requiresOwnership: true }` - weryfikacja właściciela po załadowaniu danych

## 3. Struktura komponentów
```
BrickSetEditView (views/app/BrickSetEditView.vue)
├── PageHeader (components/common/PageHeader.vue)
├── RuleLockBadge (components/bricksets/RuleLockBadge.vue) [conditional]
├── LoadingSpinner (components/common/LoadingSpinner.vue) [conditional]
├── BrickSetForm (components/bricksets/BrickSetForm.vue)
│   ├── FormField (shadcn/vue)
│   ├── Input (shadcn/vue)
│   ├── Select (shadcn/vue)
│   ├── Checkbox (shadcn/vue)
│   └── FormMessage (shadcn/vue)
├── FormActionsBar (components/bricksets/FormActionsBar.vue)
│   ├── BaseButton (components/common/BaseButton.vue) - Save
│   ├── BaseButton (components/common/BaseButton.vue) - Cancel
│   └── BaseButton (components/common/BaseButton.vue) - Delete
└── DeleteConfirmModal (components/bricksets/DeleteConfirmModal.vue) [conditional]
    ├── Dialog (shadcn/vue)
    ├── DialogHeader (shadcn/vue)
    ├── DialogContent (shadcn/vue)
    ├── DialogFooter (shadcn/vue)
    └── BaseButton (components/common/BaseButton.vue)
```

## 4. Szczegóły komponentów

### 4.1 BrickSetEditView
**Opis komponentu**: Główny kontener widoku edycji zestawu. Odpowiedzialny za zarządzanie stanem, ładowanie danych, koordynację akcji (update, delete) oraz nawigację.

**Główne elementy**:
- `PageHeader` - nagłówek z tytułem "Edytuj zestaw #{set_number}"
- `LoadingSpinner` - wyświetlany podczas ładowania danych
- `RuleLockBadge` - wyświetlany gdy `editable=false`, informuje o braku możliwości edycji
- `BrickSetForm` - formularz edycji zestawu (wypełniony danymi)
- `FormActionsBar` - pasek akcji (Zapisz, Anuluj, Usuń)
- `DeleteConfirmModal` - modal potwierdzenia usunięcia

**Obsługiwane zdarzenia**:
- `onMounted` - ładowanie danych zestawu, sprawdzenie uprawnień
- `onBeforeRouteLeave` - guard przed opuszczeniem strony z niezapisanymi zmianami
- `handleFormChange` - aktualizacja formData, wykrywanie zmian
- `handleSave` - walidacja i wysłanie PATCH request
- `handleCancel` - anulowanie edycji (confirm jeśli hasChanges)
- `handleDeleteClick` - otwarcie DeleteConfirmModal
- `handleDeleteConfirm` - wykonanie DELETE request
- `handleDeleteCancel` - zamknięcie modalu

**Warunki walidacji**:
- `editable === true` - umożliwia edycję formularza
- `deletable === true` - umożliwia usunięcie zestawu
- `hasChanges === true` - aktywuje przycisk "Zapisz"
- `isOwner === true` - użytkownik jest właścicielem zestawu

**Typy**:
- `BrickSetDetail` - dane zestawu z API
- `BrickSetFormData` - dane formularza (ViewModel)
- `BrickSetUpdateDTO` - request dla PATCH
- `ValidationErrors` - błędy walidacji z API

**Propsy**: Brak (dane z route params)

### 4.2 BrickSetForm
**Opis komponentu**: Współdzielony komponent formularza dla tworzenia i edycji zestawów. Obsługuje walidację, wyświetlanie błędów oraz emitowanie zdarzeń do rodzica.

**Główne elementy**:
- `FormField` z `Input` - numer zestawu (type="text", pattern="[0-9]{1,7}")
- `FormField` z `Select` - status produkcji (active/retired)
- `FormField` z `Checkbox` - kompletność (is_complete)
- `FormField` z `Checkbox` - instrukcja (has_instructions)
- `FormField` z `Checkbox` - pudełko (has_box)
- `FormField` z `Checkbox` - fabrycznie nowy (is_factory_new)
- `FormField` z `Input` - wstępna wycena właściciela (type="number", min="0", max="999999", opcjonalne)

**Obsługiwane zdarzenia**:
- `@update:modelValue` - emit zmiany danych formularza
- `@submit` - emit zdarzenia zapisu (po walidacji)
- `@input` (dla każdego pola) - aktualizacja formData
- `@blur` (opcjonalnie) - walidacja pola

**Warunki walidacji**:
- `set_number`: wymagane, tylko cyfry, 1-7 znaków
- `production_status`: wymagane, wartość z enuma ('active' | 'retired')
- `is_complete`: wymagane, boolean
- `has_instructions`: wymagane, boolean
- `has_box`: wymagane, boolean
- `is_factory_new`: wymagane, boolean
- `owner_initial_estimate`: opcjonalne, jeśli podane: liczba > 0 i < 1000000

**Typy**:
- `BrickSetFormData` - model danych formularza
- `ValidationErrors` - mapa błędów walidacji
- `FormMode` - 'create' | 'edit'

**Propsy**:
```typescript
interface BrickSetFormProps {
  modelValue: BrickSetFormData
  mode: FormMode
  disabled?: boolean
  validationErrors?: ValidationErrors
}
```

### 4.3 RuleLockBadge
**Opis komponentu**: Badge informacyjny wyświetlany gdy zestaw nie może być edytowany lub usunięty ze względu na reguły biznesowe.

**Główne elementy**:
- `Alert` (shadcn/vue) z wariantem "warning"
- Ikona informacji/ostrzeżenia
- Tekst wyjaśniający: "Nie możesz edytować tego zestawu, ponieważ otrzymał już wyceny od innych użytkowników lub Twoja wycena została polubiona."

**Obsługiwane zdarzenia**: Brak (komponent prezentacyjny)

**Warunki walidacji**: Brak

**Typy**: Brak

**Propsy**:
```typescript
interface RuleLockBadgeProps {
  type: 'edit' | 'delete' | 'both'
  reason?: string // opcjonalny custom message
}
```

### 4.4 FormActionsBar
**Opis komponentu**: Pasek z przyciskami akcji formularza (Zapisz, Anuluj, Usuń). Zarządza stanem aktywności przycisków oraz emituje zdarzenia do rodzica.

**Główne elementy**:
- `div.actions-bar` - kontener flex z przyciskami
- `BaseButton` variant="primary" - Zapisz
- `BaseButton` variant="ghost" - Anuluj
- `BaseButton` variant="destructive" - Usuń (po prawej stronie)

**Obsługiwane zdarzenia**:
- `@click` na "Zapisz" - emit `save`
- `@click` na "Anuluj" - emit `cancel`
- `@click` na "Usuń" - emit `delete`

**Warunki walidacji**:
- Przycisk "Zapisz" disabled gdy: `!canSave || isSaving`
- Przycisk "Usuń" disabled gdy: `!canDelete || isDeleting`
- Wszystkie przyciski disabled gdy: `isSaving || isDeleting`

**Typy**:
```typescript
interface FormActionsConfig {
  canSave: boolean
  canDelete: boolean
  isSaving: boolean
  isDeleting: boolean
}
```

**Propsy**:
```typescript
interface FormActionsBarProps {
  config: FormActionsConfig
  showDelete?: boolean // default: true
}
```

### 4.5 DeleteConfirmModal
**Opis komponentu**: Modal potwierdzenia usunięcia zestawu. Zapewnia focus trap, obsługę klawisza ESC oraz jasną komunikację o konsekwencjach akcji.

**Główne elementy**:
- `Dialog` (shadcn/vue) - kontener modalu
- `DialogHeader` - tytuł "Potwierdź usunięcie"
- `DialogContent` - treść: "Czy na pewno chcesz usunąć zestaw #{set_number}? Ta akcja jest nieodwracalna."
- `DialogFooter` - przyciski akcji
  - `BaseButton` variant="destructive" - "Usuń"
  - `BaseButton` variant="ghost" - "Anuluj"

**Obsługiwane zdarzenia**:
- `@confirm` - emit potwierdzenia usunięcia
- `@cancel` - emit anulowania (zamknięcie modalu)
- `@keydown.esc` - zamknięcie modalu
- Focus trap - focus pozostaje w modalu do zamknięcia

**Warunki walidacji**: Brak (prosty confirm w MVP)

**Typy**:
```typescript
interface DeleteConfirmData {
  brickSetNumber: string
  brickSetId: number
}
```

**Propsy**:
```typescript
interface DeleteConfirmModalProps {
  open: boolean
  data: DeleteConfirmData
  isDeleting?: boolean
}
```

## 5. Typy

### 5.1 BrickSetDetail (Response z API)
```typescript
interface BrickSetDetail {
  id: number
  set_number: string
  production_status: ProductionStatus
  is_complete: boolean
  has_instructions: boolean
  has_box: boolean
  is_factory_new: boolean
  owner_initial_estimate: number | null
  editable: boolean // kluczowe - określa czy można edytować
  deletable: boolean // kluczowe - określa czy można usunąć
  owner: {
    id: number
    username: string
  }
  valuations_count: number
  total_likes: number
  created_at: string
  updated_at: string
}
```

### 5.2 BrickSetFormData (ViewModel formularza)
```typescript
interface BrickSetFormData {
  set_number: string
  production_status: ProductionStatus
  is_complete: boolean
  has_instructions: boolean
  has_box: boolean
  is_factory_new: boolean
  owner_initial_estimate: string // string dla input, konwersja do number przed wysłaniem
}
```

### 5.3 BrickSetUpdateDTO (Request PATCH - partial)
```typescript
interface BrickSetUpdateDTO {
  set_number?: string
  production_status?: ProductionStatus
  is_complete?: boolean
  has_instructions?: boolean
  has_box?: boolean
  is_factory_new?: boolean
  owner_initial_estimate?: number | null
}
```

### 5.4 ProductionStatus (Enum)
```typescript
type ProductionStatus = 'active' | 'retired'
```

### 5.5 ValidationErrors
```typescript
interface ValidationErrors {
  set_number?: string[]
  production_status?: string[]
  is_complete?: string[]
  has_instructions?: string[]
  has_box?: string[]
  is_factory_new?: string[]
  owner_initial_estimate?: string[]
  non_field_errors?: string[]
}
```

### 5.6 FormMode
```typescript
type FormMode = 'create' | 'edit'
```

### 5.7 FormActionsConfig
```typescript
interface FormActionsConfig {
  canSave: boolean
  canDelete: boolean
  isSaving: boolean
  isDeleting: boolean
}
```

### 5.8 DeleteConfirmData
```typescript
interface DeleteConfirmData {
  brickSetNumber: string
  brickSetId: number
}
```

## 6. Zarządzanie stanem

### 6.1 Stan lokalny w BrickSetEditView
```typescript
// Routing
const route = useRoute()
const router = useRouter()
const { t } = useI18n()

// ID zestawu z parametrów route
const brickSetId = computed(() => parseInt(route.params.id as string))

// Stan danych
const brickSet = ref<BrickSetDetail | null>(null)
const formData = ref<BrickSetFormData | null>(null)
const originalData = ref<BrickSetFormData | null>(null) // do porównania zmian

// Stan UI
const isLoading = ref(true)
const isSaving = ref(false)
const isDeleting = ref(false)
const showDeleteModal = ref(false)
const validationErrors = ref<ValidationErrors>({})

// Computed properties
const isEditable = computed(() => brickSet.value?.editable ?? false)
const isDeletable = computed(() => brickSet.value?.deletable ?? false)
const hasChanges = computed(() => {
  if (!formData.value || !originalData.value) return false
  return JSON.stringify(formData.value) !== JSON.stringify(originalData.value)
})
const canSave = computed(() =>
  isEditable.value && hasChanges.value && !isSaving.value
)
const formActionsConfig = computed<FormActionsConfig>(() => ({
  canSave: canSave.value,
  canDelete: isDeletable.value,
  isSaving: isSaving.value,
  isDeleting: isDeleting.value
}))
```

### 6.2 Customowy composable: useBrickSetEdit
```typescript
// composables/useBrickSetEdit.ts
import { ref, Ref } from 'vue'
import type { BrickSetDetail, BrickSetUpdateDTO } from '@/types/brickset'

export function useBrickSetEdit(brickSetId: Ref<number>) {
  const brickSet = ref<BrickSetDetail | null>(null)
  const isLoading = ref(true)
  const error = ref<string | null>(null)

  const fetchBrickSet = async (): Promise<void> => {
    isLoading.value = true
    error.value = null
    try {
      const response = await fetch(`/api/v1/bricksets/${brickSetId.value}`, {
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      })

      if (!response.ok) {
        if (response.status === 404) {
          throw new Error('BRICKSET_NOT_FOUND')
        }
        if (response.status === 401) {
          throw new Error('NOT_AUTHENTICATED')
        }
        throw new Error('FETCH_FAILED')
      }

      brickSet.value = await response.json()
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'UNKNOWN_ERROR'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateBrickSet = async (data: BrickSetUpdateDTO): Promise<BrickSetDetail> => {
    try {
      const response = await fetch(`/api/v1/bricksets/${brickSetId.value}`, {
        method: 'PATCH',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${getAuthToken()}`
        },
        body: JSON.stringify(data)
      })

      if (!response.ok) {
        if (response.status === 403) {
          const errorData = await response.json()
          throw new Error(errorData.code || 'BRICKSET_EDIT_FORBIDDEN')
        }
        if (response.status === 400) {
          const errorData = await response.json()
          throw { type: 'VALIDATION_ERROR', errors: errorData }
        }
        throw new Error('UPDATE_FAILED')
      }

      const updated = await response.json()
      brickSet.value = updated
      return updated
    } catch (err) {
      throw err
    }
  }

  const deleteBrickSet = async (): Promise<void> => {
    try {
      const response = await fetch(`/api/v1/bricksets/${brickSetId.value}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${getAuthToken()}`
        }
      })

      if (!response.ok) {
        if (response.status === 403) {
          throw new Error('BRICKSET_DELETE_FORBIDDEN')
        }
        if (response.status === 404) {
          throw new Error('BRICKSET_NOT_FOUND')
        }
        throw new Error('DELETE_FAILED')
      }
    } catch (err) {
      throw err
    }
  }

  return {
    brickSet,
    isLoading,
    error,
    fetchBrickSet,
    updateBrickSet,
    deleteBrickSet
  }
}
```

### 6.3 Helper funkcje
```typescript
// utils/formHelpers.ts

// Konwersja BrickSetDetail -> BrickSetFormData
export function brickSetToFormData(brickSet: BrickSetDetail): BrickSetFormData {
  return {
    set_number: brickSet.set_number,
    production_status: brickSet.production_status,
    is_complete: brickSet.is_complete,
    has_instructions: brickSet.has_instructions,
    has_box: brickSet.has_box,
    is_factory_new: brickSet.is_factory_new,
    owner_initial_estimate: brickSet.owner_initial_estimate?.toString() ?? ''
  }
}

// Generowanie BrickSetUpdateDTO z tylko zmienionymi polami
export function generateUpdateDTO(
  formData: BrickSetFormData,
  originalData: BrickSetFormData
): BrickSetUpdateDTO {
  const dto: BrickSetUpdateDTO = {}

  if (formData.set_number !== originalData.set_number) {
    dto.set_number = formData.set_number
  }
  if (formData.production_status !== originalData.production_status) {
    dto.production_status = formData.production_status
  }
  if (formData.is_complete !== originalData.is_complete) {
    dto.is_complete = formData.is_complete
  }
  if (formData.has_instructions !== originalData.has_instructions) {
    dto.has_instructions = formData.has_instructions
  }
  if (formData.has_box !== originalData.has_box) {
    dto.has_box = formData.has_box
  }
  if (formData.is_factory_new !== originalData.is_factory_new) {
    dto.is_factory_new = formData.is_factory_new
  }
  if (formData.owner_initial_estimate !== originalData.owner_initial_estimate) {
    dto.owner_initial_estimate = formData.owner_initial_estimate
      ? parseFloat(formData.owner_initial_estimate)
      : null
  }

  return dto
}
```

## 7. Integracja API

### 7.1 GET /api/v1/bricksets/{id}
**Cel**: Pobranie szczegółów zestawu wraz z informacją o możliwości edycji/usunięcia.

**Request**:
- Method: `GET`
- Headers: `Authorization: Bearer {token}`
- Path params: `id: number`

**Response Success (200)**:
```typescript
BrickSetDetail // typ opisany w sekcji 5.1
```

**Response Errors**:
- `404 NOT_FOUND`: Zestaw nie istnieje
- `401 UNAUTHORIZED`: Brak autoryzacji

**Wykorzystanie**:
- `onMounted` w `BrickSetEditView`
- Wypełnienie formularza danymi
- Sprawdzenie `editable` i `deletable`

### 7.2 PATCH /api/v1/bricksets/{id}
**Cel**: Aktualizacja zestawu (tylko zmienione pola).

**Request**:
- Method: `PATCH`
- Headers:
  - `Authorization: Bearer {token}`
  - `Content-Type: application/json`
- Path params: `id: number`
- Body: `BrickSetUpdateDTO` (tylko zmienione pola)

```typescript
// Przykład body
{
  "has_box": true,
  "owner_initial_estimate": 370
}
```

**Response Success (200)**:
```typescript
BrickSetDetail // zaktualizowany obiekt
```

**Response Errors**:
- `403 BRICKSET_EDIT_FORBIDDEN`: Naruszenie reguł biznesowych (RB-01)
- `404 BRICKSET_NOT_FOUND`: Zestaw nie istnieje
- `400 VALIDATION_ERROR`: Błędy walidacji pól
  ```typescript
  {
    "set_number": ["To pole jest wymagane"],
    "owner_initial_estimate": ["Wartość musi być większa od 0"]
  }
  ```
- `401 NOT_AUTHENTICATED`: Brak autoryzacji

**Wykorzystanie**:
- Kliknięcie "Zapisz" w `FormActionsBar`
- Wysłanie tylko zmienionych pól (idempotentność)
- Obsługa błędów walidacji w formularzu

### 7.3 DELETE /api/v1/bricksets/{id}
**Cel**: Usunięcie zestawu.

**Request**:
- Method: `DELETE`
- Headers: `Authorization: Bearer {token}`
- Path params: `id: number`

**Response Success (204)**:
- No content (pusty body)

**Response Errors**:
- `403 BRICKSET_DELETE_FORBIDDEN`: Naruszenie reguł biznesowych (RB-01)
- `404 BRICKSET_NOT_FOUND`: Zestaw nie istnieje
- `401 NOT_AUTHENTICATED`: Brak autoryzacji

**Wykorzystanie**:
- Potwierdzenie w `DeleteConfirmModal`
- Redirect do `/app/bricksets` po sukcesie

## 8. Interakcje użytkownika

### 8.1 Wejście na stronę edycji
1. **Akcja**: Użytkownik klika "Edytuj" w widoku szczegółów zestawu lub bezpośrednio wchodzi na `/app/bricksets/:id/edit`
2. **Przepływ**:
   - Wyświetlenie `LoadingSpinner`
   - Wywołanie `fetchBrickSet()` (GET API)
   - Sprawdzenie `editable`:
     - Jeśli `false`: Wyświetlenie `RuleLockBadge`, toast "Nie możesz edytować tego zestawu", redirect do `/app/bricksets/:id` po 3s
     - Jeśli `true`: Wypełnienie formularza danymi, focus na pierwszym polu edytowalnym
3. **Wynik**: Formularz gotowy do edycji lub informacja o braku uprawnień

### 8.2 Edycja pól formularza
1. **Akcja**: Użytkownik zmienia wartości w polach formularza
2. **Przepływ**:
   - Event `@input` aktualizuje `formData`
   - Computed `hasChanges` porównuje z `originalData`
   - Przycisk "Zapisz" staje się aktywny gdy `hasChanges && isEditable`
   - Opcjonalnie: walidacja on blur pokazuje inline errors
3. **Wynik**: Aktualny stan formularza odzwierciedlony w UI, przycisk "Zapisz" aktywny

### 8.3 Zapisanie zmian
1. **Akcja**: Użytkownik klika przycisk "Zapisz"
2. **Przepływ**:
   - Walidacja formularza (frontend)
   - Jeśli invalid: wyświetlenie błędów, brak zapisu
   - Jeśli valid:
     - Generowanie `BrickSetUpdateDTO` (tylko zmienione pola)
     - `isSaving = true`, disable przycisków
     - Wywołanie `updateBrickSet(dto)` (PATCH API)
     - **Sukces**:
       - Aktualizacja `brickSet` i `originalData`
       - Reset `hasChanges`
       - Toast: "Zestaw zaktualizowany pomyślnie"
     - **Błąd**:
       - 403: Toast "Nie można edytować - zestaw otrzymał wyceny lub lajki", odświeżenie danych
       - 400: Wyświetlenie `validationErrors` w formularzu
       - Inne: Toast "Wystąpił błąd. Spróbuj ponownie."
     - `isSaving = false`
3. **Wynik**: Zestaw zaktualizowany lub komunikat błędu

### 8.4 Anulowanie edycji
1. **Akcja**: Użytkownik klika przycisk "Anuluj"
2. **Przepływ**:
   - Sprawdzenie `hasChanges`:
     - Jeśli `true`: Wyświetlenie confirm dialog "Masz niezapisane zmiany. Czy na pewno chcesz anulować?"
       - "Tak": Nawigacja wstecz
       - "Nie": Pozostanie na stronie
     - Jeśli `false`: Natychmiastowa nawigacja wstecz (`router.back()` lub `/app/bricksets/:id`)
3. **Wynik**: Powrót do poprzedniej strony lub pozostanie na edycji

### 8.5 Usunięcie zestawu
1. **Akcja**: Użytkownik klika przycisk "Usuń"
2. **Przepływ**:
   - Sprawdzenie `isDeletable`:
     - Jeśli `false`: Przycisk disabled (nie powinno być możliwe kliknięcie)
     - Jeśli `true`: Otwarcie `DeleteConfirmModal`
   - W modalu:
     - Wyświetlenie: "Czy na pewno chcesz usunąć zestaw #{set_number}? Ta akcja jest nieodwracalna."
     - Focus trap aktywny
     - ESC lub "Anuluj": zamknięcie modalu
     - "Usuń":
       - `isDeleting = true`, disable przycisku
       - Wywołanie `deleteBrickSet()` (DELETE API)
       - **Sukces**:
         - Zamknięcie modalu
         - Redirect do `/app/bricksets`
         - Toast: "Zestaw został usunięty"
       - **Błąd**:
         - 403: Toast "Nie można usunąć - zestaw otrzymał wyceny lub lajki", zamknięcie modalu
         - Inne: Toast "Wystąpił błąd. Spróbuj ponownie."
       - `isDeleting = false`
3. **Wynik**: Zestaw usunięty i redirect lub komunikat błędu

### 8.6 Opuszczenie strony z niezapisanymi zmianami
1. **Akcja**: Użytkownik próbuje opuścić stronę (kliknięcie linku, back button, zmiana URL)
2. **Przepływ**:
   - Router guard `onBeforeRouteLeave` sprawdza `hasChanges`
   - Jeśli `true`: Wyświetlenie confirm dialog "Masz niezapisane zmiany. Czy na pewno chcesz opuścić stronę?"
     - "Tak": Nawigacja kontynuowana
     - "Nie": Nawigacja anulowana
   - Jeśli `false`: Nawigacja bez przeszkód
3. **Wynik**: Ochrona przed utratą niezapisanych danych

## 9. Warunki i walidacja

### 9.1 Warunki biznesowe (weryfikowane przez API + frontend)

#### Warunek edycji (FR-06, RB-01)
- **Reguła**: Zestaw można edytować tylko gdy:
  - Użytkownik jest właścicielem AND
  - Brak wyceny od innego użytkownika AND
  - Wycena właściciela (jeśli istnieje) ma 0 lajków
- **Weryfikacja na frontendzie**:
  - Pole `editable: boolean` w `BrickSetDetail`
  - Komponent: `BrickSetEditView`
  - Sprawdzenie przy `onMounted`:
    ```typescript
    if (!isEditable.value) {
      showToast('Nie możesz edytować tego zestawu', 'warning')
      setTimeout(() => router.push(`/app/bricksets/${brickSetId.value}`), 3000)
    }
    ```
  - Disabled state formularza: `<BrickSetForm :disabled="!isEditable" />`
  - Przycisk "Zapisz" disabled: `canSave = isEditable && hasChanges && !isSaving`
- **Weryfikacja na backendzie**:
  - API zwróci `403 BRICKSET_EDIT_FORBIDDEN` przy próbie edycji
  - Obsługa: Toast + odświeżenie danych (stan mógł się zmienić)

#### Warunek usunięcia (FR-07, RB-01)
- **Reguła**: Taka sama jak dla edycji
- **Weryfikacja na frontendzie**:
  - Pole `deletable: boolean` w `BrickSetDetail`
  - Komponent: `FormActionsBar`
  - Przycisk "Usuń" disabled: `!isDeletable || isDeleting`
  - Opcjonalnie: ukrycie przycisku gdy `!isDeletable`
- **Weryfikacja na backendzie**:
  - API zwróci `403 BRICKSET_DELETE_FORBIDDEN`
  - Obsługa: Toast + zamknięcie modalu

### 9.2 Walidacja pól formularza

#### set_number (numer zestawu)
- **Komponent**: `BrickSetForm`
- **Warunki**:
  - Wymagane (nie może być puste)
  - Tylko cyfry
  - Długość: 1-7 znaków
- **Frontend validation**:
  ```typescript
  const validateSetNumber = (value: string): string | null => {
    if (!value) return t('validation.required')
    if (!/^\d{1,7}$/.test(value)) return t('validation.setNumberFormat')
    return null
  }
  ```
- **HTML**: `<input type="text" pattern="[0-9]{1,7}" required />`
- **Backend validation**: Zwróci 400 z polem `set_number` w errors

#### production_status (status produkcji)
- **Komponent**: `BrickSetForm`
- **Warunki**:
  - Wymagane
  - Wartość: 'active' lub 'retired'
- **Frontend validation**: Select z opcjami, brak custom walidacji (zawsze valid)
- **Backend validation**: Enum validation

#### is_complete, has_instructions, has_box, is_factory_new (checkboxy)
- **Komponent**: `BrickSetForm`
- **Warunki**: Boolean, wymagane (domyślnie false)
- **Frontend validation**: Brak (checkbox zawsze ma wartość boolean)
- **Backend validation**: Type checking

#### owner_initial_estimate (wstępna wycena)
- **Komponent**: `BrickSetForm`
- **Warunki**:
  - Opcjonalne (może być puste)
  - Jeśli podane: liczba dodatnia (> 0)
  - Maksymalna wartość: 999999
- **Frontend validation**:
  ```typescript
  const validateEstimate = (value: string): string | null => {
    if (!value) return null // opcjonalne
    const num = parseFloat(value)
    if (isNaN(num) || num <= 0) return t('validation.positiveNumber')
    if (num >= 1000000) return t('validation.maxValue', { max: 999999 })
    return null
  }
  ```
- **HTML**: `<input type="number" min="0" max="999999" step="0.01" />`
- **Backend validation**: Zwróci 400 z polem w errors

### 9.3 Wpływ warunków na UI

| Warunek | Komponent | Efekt w UI |
|---------|-----------|------------|
| `!isEditable` | `BrickSetEditView` | Wyświetlenie `RuleLockBadge`, disabled form, redirect |
| `!isDeletable` | `FormActionsBar` | Przycisk "Usuń" disabled lub ukryty |
| `!hasChanges` | `FormActionsBar` | Przycisk "Zapisz" disabled |
| `isSaving` | `FormActionsBar`, `BrickSetForm` | Wszystkie przyciski disabled, loading spinner |
| `isDeleting` | `DeleteConfirmModal` | Przycisk "Usuń" disabled, loading spinner |
| `validationErrors` | `BrickSetForm` | Inline error messages pod polami |

## 10. Obsługa błędów

### 10.1 Błędy API - GET /api/v1/bricksets/{id}

#### 404 BRICKSET_NOT_FOUND
- **Przyczyna**: Zestaw nie istnieje lub został usunięty
- **Obsługa**:
  ```typescript
  catch (error) {
    if (error.message === 'BRICKSET_NOT_FOUND') {
      showToast(t('errors.bricksetNotFound'), 'error')
      router.push('/app/bricksets')
    }
  }
  ```
- **UI**: Toast + redirect do listy zestawów

#### 401 NOT_AUTHENTICATED
- **Przyczyna**: Brak lub nieprawidłowy token
- **Obsługa**:
  ```typescript
  catch (error) {
    if (error.message === 'NOT_AUTHENTICATED') {
      authStore.logout()
      router.push(`/login?redirect=/app/bricksets/${brickSetId.value}/edit`)
    }
  }
  ```
- **UI**: Redirect do logowania z parametrem redirect

#### 403 FORBIDDEN (nie właściciel)
- **Przyczyna**: Użytkownik próbuje edytować cudzy zestaw
- **Obsługa**:
  ```typescript
  showToast(t('errors.notOwner'), 'error')
  router.push(`/app/bricksets/${brickSetId.value}`)
  ```
- **UI**: Toast + redirect do widoku szczegółów

### 10.2 Błędy API - PATCH /api/v1/bricksets/{id}

#### 403 BRICKSET_EDIT_FORBIDDEN
- **Przyczyna**: Naruszenie RB-01 (zestaw ma wyceny lub lajki)
- **Obsługa**:
  ```typescript
  catch (error) {
    if (error.message === 'BRICKSET_EDIT_FORBIDDEN') {
      showToast(t('errors.cannotEditBrickset'), 'warning')
      await fetchBrickSet() // odświeżenie stanu editable
    }
  }
  ```
- **UI**: Toast + odświeżenie danych (może pojawić się `RuleLockBadge`)

#### 400 VALIDATION_ERROR
- **Przyczyna**: Błędy walidacji pól
- **Obsługa**:
  ```typescript
  catch (error) {
    if (error.type === 'VALIDATION_ERROR') {
      validationErrors.value = error.errors
      showToast(t('errors.validationFailed'), 'error')
      // Scroll do pierwszego błędu
      scrollToFirstError()
    }
  }
  ```
- **UI**: Inline error messages w formularzu + toast

#### 404 BRICKSET_NOT_FOUND
- **Przyczyna**: Zestaw został usunięty między wejściem a zapisem
- **Obsługa**: Jak w GET (toast + redirect do listy)

### 10.3 Błędy API - DELETE /api/v1/bricksets/{id}

#### 403 BRICKSET_DELETE_FORBIDDEN
- **Przyczyna**: Naruszenie RB-01
- **Obsługa**:
  ```typescript
  catch (error) {
    if (error.message === 'BRICKSET_DELETE_FORBIDDEN') {
      showToast(t('errors.cannotDeleteBrickset'), 'warning')
      showDeleteModal.value = false
      await fetchBrickSet() // odświeżenie stanu deletable
    }
  }
  ```
- **UI**: Toast + zamknięcie modalu + odświeżenie danych

#### 404 BRICKSET_NOT_FOUND
- **Przyczyna**: Zestaw już usunięty
- **Obsługa**:
  ```typescript
  showToast(t('errors.bricksetAlreadyDeleted'), 'info')
  router.push('/app/bricksets')
  ```
- **UI**: Toast + redirect (cel osiągnięty, choć nie przez nas)

### 10.4 Błędy sieciowe

#### Network error / Timeout
- **Przyczyna**: Brak internetu, problem z serwerem
- **Obsługa**:
  ```typescript
  catch (error) {
    showToast(t('errors.networkError'), 'error')
    // Opcjonalnie: przycisk "Spróbuj ponownie"
  }
  ```
- **UI**: Toast z opcją retry

### 10.5 Błędy walidacji frontendu

#### Niezapisane zmiany przy opuszczeniu strony
- **Obsługa**: `onBeforeRouteLeave` guard
- **UI**: Confirm dialog "Masz niezapisane zmiany..."

#### Próba zapisu bez zmian
- **Obsługa**: Przycisk "Zapisz" disabled gdy `!hasChanges`
- **UI**: Brak akcji (przycisk nieaktywny)

### 10.6 Mapa błędów i komunikatów (i18n)

```typescript
// locales/pl.json
{
  "errors": {
    "bricksetNotFound": "Zestaw nie został znaleziony",
    "notOwner": "Nie masz uprawnień do edycji tego zestawu",
    "cannotEditBrickset": "Nie można edytować zestawu - otrzymał już wyceny lub lajki",
    "cannotDeleteBrickset": "Nie można usunąć zestawu - otrzymał już wyceny lub lajki",
    "validationFailed": "Sprawdź poprawność danych w formularzu",
    "networkError": "Wystąpił błąd połączenia. Sprawdź internet i spróbuj ponownie.",
    "bricksetAlreadyDeleted": "Zestaw został już usunięty",
    "unknownError": "Wystąpił nieoczekiwany błąd. Spróbuj ponownie."
  },
  "validation": {
    "required": "To pole jest wymagane",
    "setNumberFormat": "Numer zestawu może zawierać tylko cyfry (1-7 znaków)",
    "positiveNumber": "Wartość musi być większa od 0",
    "maxValue": "Wartość nie może przekraczać {max}"
  },
  "success": {
    "bricksetUpdated": "Zestaw zaktualizowany pomyślnie",
    "bricksetDeleted": "Zestaw został usunięty"
  },
  "confirm": {
    "unsavedChanges": "Masz niezapisane zmiany. Czy na pewno chcesz opuścić stronę?",
    "cancelEdit": "Czy na pewno chcesz anulować edycję?",
    "deleteBrickset": "Czy na pewno chcesz usunąć zestaw #{setNumber}? Ta akcja jest nieodwracalna."
  }
}
```

## 11. Kroki implementacji

### Krok 1: Przygotowanie typów
1. Utworzyć plik `types/brickset.ts`
2. Zdefiniować interfejsy:
   - `BrickSetDetail`
   - `BrickSetFormData`
   - `BrickSetUpdateDTO`
   - `ValidationErrors`
   - `ProductionStatus`
   - `FormMode`
   - `FormActionsConfig`
   - `DeleteConfirmData`
3. Wyeksportować wszystkie typy

### Krok 2: Implementacja composable useBrickSetEdit
1. Utworzyć plik `composables/useBrickSetEdit.ts`
2. Zaimplementować funkcje:
   - `fetchBrickSet()` - GET API
   - `updateBrickSet(dto)` - PATCH API
   - `deleteBrickSet()` - DELETE API
3. Obsługa błędów z odpowiednimi typami
4. Dodać testy jednostkowe (opcjonalnie w MVP)

### Krok 3: Utworzenie helper funkcji
1. Utworzyć plik `utils/formHelpers.ts`
2. Zaimplementować:
   - `brickSetToFormData(brickSet)` - konwersja API -> ViewModel
   - `generateUpdateDTO(formData, originalData)` - generowanie partial update
   - `validateSetNumber(value)` - walidacja numeru
   - `validateEstimate(value)` - walidacja wyceny
3. Dodać testy jednostkowe

### Krok 4: Implementacja komponentu RuleLockBadge
1. Utworzyć `components/bricksets/RuleLockBadge.vue`
2. Użyć `Alert` z shadcn/vue (variant="warning")
3. Props: `type`, `reason`
4. Teksty z i18n
5. Ikona ostrzeżenia (z lucide-vue-next)

### Krok 5: Implementacja komponentu FormActionsBar
1. Utworzyć `components/bricksets/FormActionsBar.vue`
2. Trzy `BaseButton`:
   - "Zapisz" (primary, left)
   - "Anuluj" (ghost, left)
   - "Usuń" (destructive, right)
3. Props: `config: FormActionsConfig`, `showDelete`
4. Emits: `save`, `cancel`, `delete`
5. Disabled states zgodnie z config
6. Loading states (spinner w przycisku)

### Krok 6: Implementacja komponentu DeleteConfirmModal
1. Utworzyć `components/bricksets/DeleteConfirmModal.vue`
2. Użyć `Dialog` z shadcn/vue
3. Props: `open`, `data`, `isDeleting`
4. Emits: `confirm`, `cancel`
5. Focus trap (composable `useFocusTrap`)
6. ESC handler: `@keydown.esc="$emit('cancel')"`
7. Accessibility: aria-labels, role="alertdialog"

### Krok 7: Aktualizacja komponentu BrickSetForm (jeśli nie istnieje - utworzenie)
1. Utworzyć/zaktualizować `components/bricksets/BrickSetForm.vue`
2. Props: `modelValue`, `mode`, `disabled`, `validationErrors`
3. Emits: `update:modelValue`, `submit`
4. Pola formularza (z shadcn/vue):
   - `FormField` + `Input` dla set_number
   - `FormField` + `Select` dla production_status
   - `FormField` + `Checkbox` dla boolean fields
   - `FormField` + `Input[type=number]` dla owner_initial_estimate
5. Walidacja inline (wyświetlanie `validationErrors`)
6. Obsługa `disabled` prop - wszystkie pola disabled
7. Autofocus na pierwszym polu (dyrektywa `v-focus`)

### Krok 8: Implementacja głównego widoku BrickSetEditView
1. Utworzyć `views/app/BrickSetEditView.vue`
2. Setup:
   - Import composables: `useBrickSetEdit`, `useRouter`, `useRoute`, `useI18n`
   - Definicja reactive state (jak w sekcji 6.1)
   - Computed properties: `isEditable`, `isDeletable`, `hasChanges`, `canSave`, `formActionsConfig`
3. Lifecycle hooks:
   - `onMounted`: wywołanie `fetchBrickSet()`, sprawdzenie `editable`, wypełnienie formularza
4. Metody:
   - `handleFormChange(newData)` - update formData
   - `handleSave()` - walidacja, generowanie DTO, wywołanie updateBrickSet, obsługa odpowiedzi
   - `handleCancel()` - sprawdzenie hasChanges, confirm jeśli true, nawigacja
   - `handleDeleteClick()` - otwarcie modalu
   - `handleDeleteConfirm()` - wywołanie deleteBrickSet, obsługa odpowiedzi
   - `handleDeleteCancel()` - zamknięcie modalu
5. Router guard:
   - `onBeforeRouteLeave`: sprawdzenie hasChanges, confirm jeśli true
6. Template:
   - Conditional rendering: loading, ruleLockBadge, form, modal
   - Binding propsów do komponentów dzieci
   - Event handlers

### Krok 9: Dodanie routingu
1. Edytować `router/index.ts`
2. Dodać route:
   ```typescript
   {
     path: '/app/bricksets/:id/edit',
     name: 'BrickSetEdit',
     component: () => import('@/views/app/BrickSetEditView.vue'),
     meta: {
       requiresAuth: true,
       title: 'Edytuj zestaw'
     }
   }
   ```
3. Opcjonalnie: guard sprawdzający ownership (alternatywa: sprawdzenie w komponencie)

### Krok 10: Dodanie tekstów i18n
1. Edytować `locales/pl.json`
2. Dodać wszystkie klucze z sekcji 10.6:
   - `errors.*`
   - `validation.*`
   - `success.*`
   - `confirm.*`
3. Dodać etykiety pól formularza:
   - `brickset.setNumber`, `brickset.productionStatus`, etc.

### Krok 11: Implementacja toast notifications (jeśli nie istnieje)
1. Utworzyć `composables/useToast.ts` lub użyć biblioteki (np. vue-toastification)
2. Funkcja `showToast(message, type)` dostępna globalnie
3. Typy: success, error, warning, info
4. Konfiguracja: pozycja (top-right), czas (5s dla info/success, 7s dla error/warning)

### Krok 12: Stylowanie Tailwind
1. Dla `BrickSetEditView`:
   - Container: `max-w-2xl mx-auto p-6`
   - Spacing między sekcjami: `space-y-6`
2. Dla `FormActionsBar`:
   - Layout: `flex justify-between items-center`
   - Left buttons: `flex gap-2`
3. Dla `RuleLockBadge`:
   - Margin: `mb-6`
   - Padding: `p-4`
4. Dla `DeleteConfirmModal`:
   - Max width: `max-w-md`
   - Padding: `p-6`

### Krok 13: Accessibility (A11y)
1. Dodać `aria-labels` do wszystkich przycisków
2. `role="alertdialog"` dla DeleteConfirmModal
3. Focus trap w modalu (composable `useFocusTrap`)
4. Autofocus na pierwszym polu formularza (dyrektywa)
5. Keyboard navigation: ESC zamyka modal, Enter submituje formularz
6. Screen reader announcements dla toast notifications

### Krok 14: Testowanie manualne
1. **Test 1**: Edycja zestawu bez wycen/lajków
   - Wejście na edit, zmiana pól, zapis
   - Weryfikacja: dane zaktualizowane, toast sukcesu
2. **Test 2**: Próba edycji zestawu z wycenami
   - Mock: `editable=false`
   - Weryfikacja: RuleLockBadge, disabled form, redirect
3. **Test 3**: Usunięcie zestawu
   - Kliknięcie Delete, potwierdzenie w modalu
   - Weryfikacja: redirect do listy, toast sukcesu, zestaw nie istnieje
4. **Test 4**: Próba usunięcia zestawu z lajkami
   - Mock: `deletable=false`
   - Weryfikacja: przycisk disabled, API zwraca 403, toast błędu
5. **Test 5**: Niezapisane zmiany
   - Zmiana pola, próba opuszczenia strony
   - Weryfikacja: confirm dialog, możliwość anulowania
6. **Test 6**: Błędy walidacji
   - Nieprawidłowy numer zestawu, ujemna wycena
   - Weryfikacja: inline errors, toast, brak zapisu
7. **Test 7**: Błędy sieciowe
   - Symulacja 500, timeout
   - Weryfikacja: toast błędu, możliwość retry

### Krok 15: Testy automatyczne (opcjonalnie w MVP, rekomendowane)
1. **Unit tests** (Vitest):
   - `useBrickSetEdit.spec.ts` - testy composable
   - `formHelpers.spec.ts` - testy funkcji pomocniczych
2. **Component tests** (Vue Test Utils):
   - `BrickSetForm.spec.vue` - renderowanie, emitowanie zdarzeń
   - `FormActionsBar.spec.vue` - disabled states, clicks
   - `DeleteConfirmModal.spec.vue` - focus trap, ESC, confirm
3. **E2E tests** (Playwright - opcjonalnie):
   - Pełny flow: wejście -> edycja -> zapis -> weryfikacja
   - Flow usunięcia: wejście -> delete -> confirm -> redirect

### Krok 16: Dokumentacja
1. Utworzyć `docs/components/BrickSetEditView.md`:
   - Opis widoku
   - Propsy i emity wszystkich komponentów
   - Przykłady użycia
   - Known issues / limitations
2. Zaktualizować `CHANGELOG.md` z nową funkcjonalnością
3. Dodać entry do `docs/user-guide.md` (jeśli istnieje)

### Krok 17: Code review i refaktoryzacja
1. Przegląd kodu pod kątem:
   - DRY (Don't Repeat Yourself)
   - Separacja odpowiedzialności (concerns)
   - Performance (memoization, lazy loading)
   - Accessibility
   - Error handling completeness
2. Refaktoryzacja jeśli potrzebna
3. Commit i push do brancha feature

### Krok 18: Integracja z istniejącym kodem
1. Dodać link "Edytuj" w `BrickSetDetailView`:
   ```vue
   <BaseButton
     v-if="brickSet.editable"
     @click="router.push(`/app/bricksets/${brickSet.id}/edit`)"
   >
     Edytuj
   </BaseButton>
   ```
2. Dodać link do nawigacji (jeśli dotyczy)
3. Zaktualizować breadcrumbs (jeśli używane)

### Krok 19: Deploy i monitoring
1. Deploy na środowisko testowe
2. Testowanie przez zespół QA / Product Owner
3. Monitoring błędów (np. Sentry):
   - Tracking 403 errors
   - Tracking validation errors
   - Tracking network errors
4. Analytics (opcjonalnie):
   - Event: "brickset_edited"
   - Event: "brickset_deleted"
   - Event: "edit_blocked_by_rule"

### Krok 20: Iteracja na podstawie feedbacku
1. Zbieranie feedbacku od użytkowników testowych
2. Priorytetyzacja poprawek i ulepszeń
3. Implementacja w kolejnych iteracjach
4. Merge do main branch po akceptacji

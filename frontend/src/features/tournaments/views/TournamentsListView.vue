<template>
  <section class="page-shell">
    <ui-card :is-error="isError">
      <template #header>
        <div class="tournaments-header">
          <h1 class="tournaments-title">Tournaments list</h1>
          <ui-button
            v-if="user?.role === 'admin'"
            size="sm"
            asLink
            to="/tournaments/create"
            class="create-new-btn"
            >Create new</ui-button
          >
        </div>
      </template>

      <template #error>
        <div style="display: flex; height: 300px; justify-content: center; align-items: center">
          <p>Error while fetching tournaments (code: {{ error?.code }})</p>
        </div>
      </template>

      <div>
        <div class="search-wrapper">
          <ui-input
            v-model="searchInput"
            class="search-input"
            placeholder="Search tournament by name"
            @keydown.enter="applySearch"
          />

          <ui-button v-if="searchInput.length >= 2" @click="applySearch"><arrow-right /></ui-button>
        </div>

        <ui-skeleton-loader :loading="isLoading || isFetching">
          <template #skeleton>
            <div class="tournaments-grid">
              <ui-card v-for="i in pageSize" :key="i" class="tournament-card">
                <template #header>
                  <ui-skeleton variant="rect" width="70%" height="24px" />
                </template>

                <ui-skeleton variant="rect" class="tournaments-description" height="48px" />

                <div class="tournaments-meta">
                  <div class="tournaments-date">
                    <ui-skeleton variant="rect" width="60px" />
                    <ui-skeleton variant="rect" width="130px" />
                  </div>

                  <ui-skeleton variant="rect" width="120px" height="28px" />
                </div>

                <ui-skeleton variant="rect" width="100%" height="36px" />
              </ui-card>
            </div>
          </template>

          <div>
            <template v-if="pageItems.length">
              <div class="tournaments-grid">
                <ui-card
                  v-for="tournament in pageItems"
                  :key="tournament.id"
                  class="tournament-card"
                >
                  <template #header>
                    <h3>{{ tournament.name }}</h3>
                  </template>

                  <div>
                    <p class="tournaments-description" :title="tournament.description">
                      {{ truncateText(tournament.description, 200) }}
                    </p>

                    <div class="tournaments-meta">
                      <div class="tournaments-date">
                        <p>Start date:</p>

                        <p>
                          {{
                            tournament.startAt.toLocaleDateString('en-US', {
                              month: 'long',
                              day: 'numeric',
                              year: 'numeric',
                            })
                          }}
                        </p>
                      </div>

                      <ui-badge variant="green">
                        {{ tournament.status }}
                      </ui-badge>
                    </div>
                  </div>

                  <template #footer>
                    <ui-button
                      size="sm"
                      asLink
                      :to="`/tournaments/${tournament.id}`"
                      variant="secondary"
                      class="tournaments-details-btn"
                    >
                      View details
                    </ui-button>
                  </template>
                </ui-card>
              </div>
            </template>

            <div v-if="totalPages > 1" class="pagination">
              <ui-button size="sm" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)">
                Prev
              </ui-button>

              <ui-button
                v-for="page in visiblePages"
                :key="`${page}`"
                size="sm"
                class="pagination-btn"
                :disabled="page === '...'"
                :variant="page === currentPage ? 'default' : 'secondary'"
                @click="typeof page === 'number' && goToPage(page)"
              >
                {{ page }}
              </ui-button>

              <ui-button
                size="sm"
                :disabled="currentPage === totalPages"
                @click="goToPage(currentPage + 1)"
              >
                Next
              </ui-button>
            </div>
          </div>
        </ui-skeleton-loader>
      </div>
    </ui-card>
  </section>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'

import UiCard from '@/components/UiCard.vue'
import UiBadge from '@/components/UiBadge.vue'
import UiButton from '@/components/UiButton.vue'
import UiSkeletonLoader from '@/components/UiSkeletonLoader.vue'
import UiSkeleton from '@/components/UiSkeleton.vue'
import UiInput from '@/components/UiInput.vue'
import ArrowRight from '@/icons/ArrowRight.vue'
import { parseApiError } from '@/api'
import { truncateText } from '@/lib/utils'
import { useProfile } from '@/queries/accounts'

interface Data {
  id: number
  name: string
  description: string
  status: string
  startAt: Date
}

interface Response {
  data: Data[]
  page: number
  total: number
}

const pageSize = 12
const totalMockedItems = 120

const currentPage = ref(1)
const searchInput = ref('')
const searchQuery = ref('')

const { data: user } = useProfile()

const fetchItems = async (page: number, query?: string): Promise<Response> => {
  await new Promise((resolve) => setTimeout(resolve, 500))

  const allItems = Array.from({ length: totalMockedItems }, (_, i) => ({
    id: i + 1,
    name: `Item ${i + 1}`,
    description: `"Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum." ${i + 1}`,
    status: Math.random() > 0.5 ? 'Running' : 'Registration open',
    startAt: new Date(Date.now() + i * 86400000),
  }))

  let filtered = allItems

  if (query?.trim()) {
    const normalized = query.trim().toLowerCase()

    filtered = allItems.filter((item) => item.name.toLowerCase().includes(normalized))
  }

  const total = filtered.length

  const start = (page - 1) * pageSize
  const end = start + pageSize

  const data = filtered.slice(start, end)

  return {
    data,
    page,
    total,
  }
}

const {
  data,
  isLoading,
  isFetching,
  error: tournamentsError,
  isError,
} = useQuery({
  queryKey: computed(() => ['items', currentPage.value, searchQuery.value]),
  queryFn: () => fetchItems(currentPage.value, searchQuery.value),
  staleTime: 1000 * 60 * 5,
})
const error = computed(() => parseApiError(tournamentsError.value))

const pageItems = computed(() => data.value?.data ?? [])
const totalPages = computed(() => Math.ceil((data.value?.total ?? 0) / pageSize))

const visiblePages = computed(() => {
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    return Array.from({ length: total }, (_, i) => i + 1)
  }

  if (current <= 4) {
    return [1, 2, 3, 4, 5, '...', total]
  }

  if (current >= total - 3) {
    return [1, '...', total - 4, total - 3, total - 2, total - 1, total]
  }

  return [1, '...', current - 1, current, current + 1, '...', total]
})

const goToPage = (page: number) => {
  if (page < 1 || page > totalPages.value) {
    return
  }

  currentPage.value = page
}

const applySearch = () => {
  currentPage.value = 1
  searchQuery.value = searchInput.value
}
</script>

<style scoped>
.tournaments-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.search-wrapper {
  display: flex;
  justify-content: space-between;
  gap: 0.3rem;
  margin-bottom: 1rem;
}

.search-input {
  flex: 1;
}

.tournaments-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.tournaments-description {
  margin-bottom: 12px;
  line-height: 1.5;
}

.tournament-card {
  background: var(--muted) !important;
}

.tournaments-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  color: var(--muted-foreground);
}

.tournaments-date {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tournaments-date p {
  margin: 0;
}

.tournaments-details-btn {
  width: 100%;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 24px;
}

.pagination-btn {
  width: 40px;
  min-width: 40px;
  height: 40px;
  padding: 0;
}

@media (max-width: 1024px) {
  .tournaments-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .tournaments-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .tournaments-meta {
    flex-direction: column;
    align-items: flex-start;
  }

  .pagination {
    gap: 6px;
    margin-top: 20px;
  }
}

@media (max-width: 480px) {
  .pagination {
    flex-wrap: nowrap;
    overflow-x: auto;
    padding-bottom: 4px;
  }

  .tournaments-header {
    flex-direction: column;
    align-items: start;
  }

  .create-new-btn {
    width: 100%;
  }
}
</style>

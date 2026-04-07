<template>
  <ui-card v-if="isCaptain" class="manage-zone">
    <div class="manage-row">
      <div>
        <h3>Edit team</h3>
        <p class="text-muted">Update team profile and manage members in edit workspace.</p>
      </div>
      <ui-button asLink variant="outline" size="sm" :to="`/teams/${team?.id}/edit`"
        >Edit team</ui-button
      >
    </div>

    <div class="danger-zone-header">
      <danger-icon />
      <span>Danger Zone</span>
    </div>

    <div class="danger-zone-box">
      <div class="manage-row danger">
        <div>
          <h3>Change visibility</h3>
          <p class="text-muted">
            <ui-badge :variant="team?.is_public ? 'green' : 'red'">{{
              team?.is_public ? 'Public' : 'Private'
            }}</ui-badge>
            -

            {{
              team?.is_public
                ? 'Anyone can find and request to join this team.'
                : 'Only invited members can see this team.'
            }}
          </p>
        </div>

        <TeamVisibilityModal
          :team="props.team"
          @changed-team-visibility="(newTeamValue) => emit('updateTeam', newTeamValue)"
        />
      </div>

      <div class="manage-row danger">
        <div>
          <h3>Delete team</h3>
          <p class="text-muted">This action permanently deletes the team and cannot be undone.</p>
        </div>

        <DeleteTeamModal
          :disabled="props.loading"
          :team="props.team"
          @deleted="router.push('/teams')"
        />
      </div>
    </div>
  </ui-card>
</template>

<script setup lang="ts">
import type { GetTeamInfoResponse } from '@/api/teams/types'
import DeleteTeamModal from './modals/DeleteTeamModal.vue'
import TeamVisibilityModal from './modals/TeamVisibilityModal.vue'
import UiCard from '@/components/UiCard.vue'
import DangerIcon from '@/icons/DangerIcon.vue'
import UiButton from '@/components/UiButton.vue'
import UiBadge from '@/components/UiBadge.vue'
import { useRouter } from 'vue-router'

interface Props {
  team?: GetTeamInfoResponse
  loading: boolean
  isCaptain: boolean
}

const props = defineProps<Props>()
const router = useRouter()

const emit = defineEmits<{
  (e: 'updateTeam', newTeamValue: GetTeamInfoResponse): void
}>()
</script>

<style scoped>
.manage-zone {
  border: 1px solid var(--line-soft);
  overflow: hidden;
}

.danger-zone-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.55rem 0.8rem;
  margin: 0.2rem 0 0;
  background: rgba(220, 38, 38, 0.06);
  border: 1px solid rgba(220, 38, 38, 0.2);
  border-radius: 8px;
  color: #991b1b;
  font-size: 0.78rem;
  font-weight: 800;
  letter-spacing: 0.07em;
  text-transform: uppercase;
}

.danger-zone-icon {
  width: 0.95rem;
  height: 0.95rem;
  flex-shrink: 0;
}

.danger-zone-box {
  margin-top: 0.6rem;
  border: 1px solid rgba(220, 38, 38, 0.22);
  border-radius: 10px;
  overflow: hidden;
  background: rgba(254, 226, 226, 0.18);
}

.danger-zone-box .manage-row {
  padding: 1rem;
  border-top: 1px solid rgba(220, 38, 38, 0.14);
}

.manage-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.9rem;
  padding: 0 0 1rem 0;
}

.manage-row + .manage-row {
  border-top: 1px solid var(--line-soft);
}

.manage-row h3 {
  margin: 0;
  font-size: 1rem;
}

.manage-row p {
  margin: 0.3rem 0 0;
}

.manage-row.danger h3 {
  color: #991b1b;
}
</style>

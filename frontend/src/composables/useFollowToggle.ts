import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { toast } from 'vue-sonner'
import { useAuthStore } from '@/stores/auth'
import { useFollowUser, useUnfollowUser } from '@/api/users'

// PublicUserOut arama/öneri sonuçlarında is_following taşımıyor (yalnız ProfileOut/
// PublicUserWithFollowOut taşıyor); bu yüzden önceden takip edilen biri bu oturumda ilk
// görüldüğünde "Takip et" gösterir — tıklanınca yerel olarak işaretlenir (follow idempotent).
export function useFollowToggle() {
  const auth = useAuthStore()
  const router = useRouter()
  const followMutation = useFollowUser()
  const unfollowMutation = useUnfollowUser()

  const followedThisSession = ref(new Set<string>())
  const pendingUsername = ref<string | null>(null)

  function isFollowing(username: string): boolean {
    return followedThisSession.value.has(username)
  }

  function isPending(username: string): boolean {
    return pendingUsername.value === username
  }

  async function toggle(username: string) {
    if (!auth.isAuthenticated) {
      toast.info('Bunun için giriş yapmalısın')
      void router.push({ path: '/giris', query: { redirect: router.currentRoute.value.fullPath } })
      return
    }
    const wasFollowing = isFollowing(username)
    pendingUsername.value = username
    try {
      if (wasFollowing) {
        await unfollowMutation.mutateAsync(username)
        followedThisSession.value.delete(username)
      } else {
        await followMutation.mutateAsync(username)
        followedThisSession.value.add(username)
      }
    } catch {
      toast.error('Bir şeyler ters gitti, tekrar dene')
    } finally {
      pendingUsername.value = null
    }
  }

  return { isFollowing, isPending, toggle }
}

package de.provoware.naqya

data class BridgeEnvelope(val id: String, val action: String)

object BridgeContract {
    val allowedActions = setOf(
        "platformInfo", "shareText", "scheduleReminder", "cancelReminder", "audioStart", "audioStop", "acceptanceResult"
    )
    fun isAllowed(action: String): Boolean = action in allowedActions
}

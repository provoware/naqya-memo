import Foundation

struct BridgeEnvelope: Codable {
    let id: String
    let action: String
}

enum BridgeContract {
    static let allowedActions: Set<String> = [
        "platformInfo", "shareText", "scheduleReminder", "cancelReminder", "audioStart", "audioStop", "acceptanceResult"
    ]
    static func isAllowed(_ action: String) -> Bool { allowedActions.contains(action) }
}

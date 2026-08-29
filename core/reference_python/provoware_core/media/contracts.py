
def android_media_contract():
    return {"platform":"android","microphone_permission":"android.permission.RECORD_AUDIO",
            "runtime_permission_required":True,"capture_api":"MediaRecorder/AudioRecord adapter",
            "packaging_status":"BUILD_STRUCTURE_ONLY","native_build_tested":False}

def ios_media_contract():
    return {"platform":"ios","microphone_permission":"NSMicrophoneUsageDescription",
            "runtime_permission_required":True,"capture_api":"AVAudioRecorder adapter",
            "packaging_status":"BUILD_CONCEPT_ONLY","native_build_tested":False}

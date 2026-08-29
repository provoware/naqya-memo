package de.provoware.naqya

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log

class ReminderReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val manager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val channelId = "provoware_reminders"
        if (Build.VERSION.SDK_INT >= 26) manager.createNotificationChannel(
            NotificationChannel(channelId, "Erinnerungen", NotificationManager.IMPORTANCE_DEFAULT)
        )
        val open = PendingIntent.getActivity(
            context, 0, Intent(context, MainActivity::class.java),
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val notification = android.app.Notification.Builder(context, channelId)
            .setSmallIcon(R.drawable.ic_notification)
            .setContentTitle(intent.getStringExtra("title") ?: "Erinnerung")
            .setContentText(intent.getStringExtra("body") ?: "")
            .setContentIntent(open)
            .setAutoCancel(true)
            .build()
        manager.notify(intent.getStringExtra("entity_id")?.hashCode() ?: 1, notification)
        Log.i("ProvowareAcceptance", "REMINDER_FIRED:" + (intent.getStringExtra("entity_id") ?: "unknown"))
    }
}

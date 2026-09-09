
.class public Lcom/megalodon/payload/MainActivity;
.super Landroid/app/Activity;
.source "MainActivity.smali"

.method public constructor <init>()V
    .registers 1
    invoke-direct {{p0}}, Landroid/app/Activity;-><init>()V
    return-void
.end method

.method public onCreate(Landroid/os/Bundle;)V
    .registers 5
    invoke-super {{p0, p1}}, Landroid/app/Activity;->onCreate(Landroid/os/Bundle;)V
    
    new-instance v0, Landroid/content/Intent;
    const-class v1, Lcom/megalodon/payload/PayloadService;
    invoke-direct {{v0, p0, v1}}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V
    invoke-virtual {{p0, v0}}, Lcom/megalodon/payload/MainActivity;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;
    
    invoke-virtual {{p0}}, Lcom/megalodon/payload/MainActivity;->finish()V
    return-void
.end method
.end class

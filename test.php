<?php
ini_set('display_errors', 1);
error_reporting(E_ALL);

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $new_ip = $_POST['new_ip'] ?? '';
    if (filter_var($new_ip, FILTER_VALIDATE_IP, FILTER_FLAG_IPV4)) {
        $output = shell_exec("sudo /usr/local/bin/change_ip.sh " . escapeshellarg($new_ip) . " 2>&1");
        echo "<h3>Adresse IP modifiée en : $new_ip</h3>";
        echo "<pre>$output</pre>";
    } else {
        echo "<h3 style='color:red;'>Adresse IP invalide !</h3>";
    }
}
?>
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Changer l'adresse IP de la Box</title>
</head>
<body>
    <h2>Changer l'adresse IP de la Box</h2>
    <form method="post">
        Nouvelle IP :
        <input type="text" name="new_ip" placeholder="ex: 192.168.1.10" required>
        <button type="submit">Changer</button>
    </form>
</body>
</html>

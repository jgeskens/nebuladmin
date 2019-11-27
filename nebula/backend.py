import subprocess
import tempfile
import os


def generate_network_credentials(name):
    with tempfile.TemporaryDirectory() as temp_dir:
        p = subprocess.Popen([
            '/go/bin/nebula-cert', 'ca',
            '-name', f'"{name}"',
            '-out-crt', os.path.join(temp_dir, 'ca.crt'),
            '-out-key', os.path.join(temp_dir, 'ca.key'),
        ])
        out, err = p.communicate()

        with open(os.path.join(temp_dir, 'ca.crt'), 'rb') as crt_fh:
            crt = crt_fh.read().decode('utf-8')
        with open(os.path.join(temp_dir, 'ca.key'), 'rb') as key_fh:
            key = key_fh.read().decode('utf-8')

    return {'crt': crt, 'key': key}


def generate_member_credentials(name, ip, ca_crt, ca_key):
    with tempfile.TemporaryDirectory() as temp_dir:
        with open(os.path.join(temp_dir, 'ca.crt'), 'wb') as ca_crt_fh:
            ca_crt_fh.write(ca_crt.encode('utf-8'))
        with open(os.path.join(temp_dir, 'ca.key'), 'wb') as ca_key_fh:
            ca_key_fh.write(ca_key.encode('utf-8'))

        p = subprocess.Popen([
            '/go/bin/nebula-cert', 'sign',
            '-ca-crt', os.path.join(temp_dir, 'ca.crt'),
            '-ca-key', os.path.join(temp_dir, 'ca.key'),
            '-name', f'"{name}"',
            '-ip', f'{ip}',
            '-out-crt', os.path.join(temp_dir, 'member.crt'),
            '-out-key', os.path.join(temp_dir, 'member.key'),
        ])
        out, err = p.communicate()

        with open(os.path.join(temp_dir, 'member.crt'), 'rb') as crt_fh:
            crt = crt_fh.read().decode('utf-8')
        with open(os.path.join(temp_dir, 'member.key'), 'rb') as key_fh:
            key = key_fh.read().decode('utf-8')

    return {'crt': crt, 'key': key}

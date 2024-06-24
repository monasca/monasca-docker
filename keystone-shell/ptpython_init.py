import keystone_shell_vars

keystone = keystone_shell_vars.get_keystone_client()
ks = keystone

kubernetes = keystone_shell_vars.get_kubernetes_client()
k8s = kubernetes

print('--------------------------------------')
print('Pre-defined variables:')
print(' - keystone (ks): keystone client')
print(' - kubernetes (k8s): kubernetes client')
print('--------------------------------------')

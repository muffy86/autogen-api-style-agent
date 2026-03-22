import type { AppDefinition } from '$lib/types';

class AppRegistry {
  apps = $state<AppDefinition[]>([
    {
      id: 'chat',
      name: 'Chat',
      icon: 'message-square',
      description: 'AI-powered conversations',
      defaultWidth: 800,
      defaultHeight: 550,
      minWidth: 500,
      minHeight: 400,
      singleton: true
    },
    {
      id: 'files',
      name: 'Files',
      icon: 'folder',
      description: 'Browse and manage files',
      defaultWidth: 850,
      defaultHeight: 550,
      minWidth: 600,
      minHeight: 400,
      singleton: true
    },
    {
      id: 'terminal',
      name: 'Terminal',
      icon: 'terminal',
      description: 'Command line interface',
      defaultWidth: 700,
      defaultHeight: 450,
      minWidth: 400,
      minHeight: 300,
      singleton: false
    },
    {
      id: 'settings',
      name: 'Settings',
      icon: 'settings',
      description: 'System preferences',
      defaultWidth: 750,
      defaultHeight: 500,
      minWidth: 550,
      minHeight: 400,
      singleton: true
    },
    {
      id: 'search',
      name: 'Search',
      icon: 'search',
      description: 'Spotlight search & quick actions',
      defaultWidth: 600,
      defaultHeight: 400,
      minWidth: 400,
      minHeight: 300,
      singleton: true
    }
  ]);

  getApp(id: string): AppDefinition | undefined {
    return this.apps.find((a) => a.id === id);
  }
}

export const appRegistry = new AppRegistry();

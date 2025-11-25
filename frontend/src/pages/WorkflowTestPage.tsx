import { useState } from 'react';
import { AgentActivityPanel } from '../components/workflow';
import { useWorkflow } from '../lib/context';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';

/**
 * Test page for workflow components
 * This demonstrates how to use the workflow system
 */
export function WorkflowTestPage() {
  const {
    workflowState,
    startCreateWorkflow,
    isCreating,
  } = useWorkflow();

  const [sessionId, setSessionId] = useState('test-session-123');
  const [requirements, setRequirements] = useState('Create a modern landing page with a hero section, features grid, and contact form');
  const [framework, setFramework] = useState<string>('react');
  const [designStyle, setDesignStyle] = useState<string>('modern');

  const handleStartWorkflow = async () => {
    await startCreateWorkflow({
      session_id: sessionId,
      requirements,
      framework: framework as any,
      design_style: designStyle as any,
      features: ['responsive', 'dark-mode', 'animations'],
    });
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="space-y-2">
        <h1 className="text-3xl font-bold">Workflow Test Page</h1>
        <p className="text-muted-foreground">
          Test the workflow execution and monitoring system
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <Card>
          <CardHeader>
            <CardTitle>Start Workflow</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="session-id">Session ID</Label>
              <Input
                id="session-id"
                value={sessionId}
                onChange={(e) => setSessionId(e.target.value)}
                placeholder="Enter session ID"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="requirements">Requirements</Label>
              <Textarea
                id="requirements"
                value={requirements}
                onChange={(e) => setRequirements(e.target.value)}
                placeholder="Describe what you want to build..."
                rows={4}
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="framework">Framework</Label>
              <Select value={framework} onValueChange={setFramework}>
                <SelectTrigger id="framework">
                  <SelectValue placeholder="Select framework" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="react">React</SelectItem>
                  <SelectItem value="vue">Vue</SelectItem>
                  <SelectItem value="nextjs">Next.js</SelectItem>
                  <SelectItem value="html">HTML</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div className="space-y-2">
              <Label htmlFor="design-style">Design Style</Label>
              <Select value={designStyle} onValueChange={setDesignStyle}>
                <SelectTrigger id="design-style">
                  <SelectValue placeholder="Select design style" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="modern">Modern</SelectItem>
                  <SelectItem value="minimal">Minimal</SelectItem>
                  <SelectItem value="corporate">Corporate</SelectItem>
                  <SelectItem value="creative">Creative</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <Button
              onClick={handleStartWorkflow}
              disabled={isCreating || !!workflowState}
              className="w-full"
            >
              {isCreating ? 'Starting...' : 'Start Workflow'}
            </Button>

            {workflowState && (
              <div className="text-sm text-muted-foreground">
                Workflow ID: <code className="font-mono">{workflowState.workflow_id}</code>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Workflow Activity Panel */}
        <AgentActivityPanel
          onCancel={() => console.log('Workflow cancelled')}
          showLogs={true}
        />
      </div>
    </div>
  );
}

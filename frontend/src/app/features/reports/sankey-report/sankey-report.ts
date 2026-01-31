import { Component, inject, OnInit, signal, computed, ElementRef, viewChild, afterNextRender, Injector } from '@angular/core';
import { Router } from '@angular/router';
import { JobApplicationService } from '../../../core/services/job-application.service';
import { ApplicationStatus } from '../../../core/models/application-status.enum';
import * as d3 from 'd3';
import { sankey, sankeyLinkHorizontal, SankeyNode, SankeyLink } from 'd3-sankey';

type SankeyStatus = ApplicationStatus | 'RESPONDED' | 'NO RESPONSE';

interface SankeyTransition {
  from: SankeyStatus;
  to: SankeyStatus;
  count: number;
}

interface NodeExtra {
  name: string;
  status: SankeyStatus;
}

interface LinkExtra {
  count: number;
}

type SNode = SankeyNode<NodeExtra, LinkExtra>;
type SLink = SankeyLink<NodeExtra, LinkExtra>;

@Component({
  selector: 'app-sankey-report',
  imports: [],
  templateUrl: './sankey-report.html',
  styleUrl: './sankey-report.css'
})
export class SankeyReportComponent implements OnInit {
  private readonly service = inject(JobApplicationService);
  private readonly router = inject(Router);
  private readonly injector = inject(Injector);

  readonly chartContainer = viewChild<ElementRef<HTMLDivElement>>('chartContainer');

  isLoading = signal(true);
  error = signal<string | null>(null);

  private readonly respondedStatuses: ReadonlySet<ApplicationStatus> = new Set([
    ApplicationStatus.REJECTED,
    ApplicationStatus.SCREEN,
    ApplicationStatus.INTERVIEW
  ]);

  private readonly interviewStatuses: ReadonlySet<ApplicationStatus> = new Set([
    ApplicationStatus.SCREEN,
    ApplicationStatus.INTERVIEW
  ]);

  private readonly statusColors: Record<SankeyStatus, string> = {
    [ApplicationStatus.APPLIED]: '#2196f3',
    [ApplicationStatus.SCREEN]: '#ff9800',
    [ApplicationStatus.INTERVIEW]: '#9c27b0',
    [ApplicationStatus.OFFER]: '#4caf50',
    [ApplicationStatus.REJECTED]: '#f44336',
    [ApplicationStatus.WITHDRAWN]: '#757575',
    [ApplicationStatus.NOOFFER]: '#607d8b',
    'RESPONDED': '#b9ad05',
    'NO RESPONSE': '#00bcd4'
  };

  transitions = computed<SankeyTransition[]>(() => {
    const apps = this.service.applications();
    const transitionMap = new Map<string, SankeyTransition>();

    const appliedNoresponseKey = 'APPLIED->NO RESPONSE';
    const appliedRespondedKey = 'APPLIED->RESPONDED';
    const respondedRejectedKey = 'RESPONDED->REJECTED';
    const respondedInterviewKey = 'RESPONDED->INTERVIEW';
    const interviewOfferKey = 'INTERVIEW->OFFER';
    const interviewNoofferKey = 'INTERVIEW->NO OFFER';

    for (const app of apps) {
      if (app.status.length === 0) continue;

      if (app.status.length === 1) {
        this.addTransition(appliedNoresponseKey, { from: ApplicationStatus.APPLIED, to: 'NO RESPONSE', count: 1 }, transitionMap);
        continue;
      }

      const response = app.status.find(s => this.respondedStatuses.has(s.status));
      if (response) {
        this.addTransition(appliedRespondedKey, { from: ApplicationStatus.APPLIED, to: 'RESPONDED', count: 1 }, transitionMap);
      }

      const rejected = app.status.find(s => s.status === ApplicationStatus.REJECTED);
      if (rejected) {
        this.addTransition(respondedRejectedKey, { from: 'RESPONDED', to: ApplicationStatus.REJECTED, count: 1 }, transitionMap);
        continue;
      }

      const interview = app.status.find(s => this.interviewStatuses.has(s.status));
      if (interview) {
        this.addTransition(respondedInterviewKey, { from: 'RESPONDED', to: ApplicationStatus.INTERVIEW, count: 1 }, transitionMap);
      }

      const offer = app.status.find(s => s.status === ApplicationStatus.OFFER);
      if (offer) {
        this.addTransition(interviewOfferKey, { from: ApplicationStatus.INTERVIEW, to: ApplicationStatus.OFFER, count: 1 }, transitionMap);
      } else {
        this.addTransition(interviewNoofferKey, { from: ApplicationStatus.INTERVIEW, to: ApplicationStatus.NOOFFER, count: 1 }, transitionMap);
      }
    }

    return Array.from(transitionMap.values()).sort((a, b) => b.count - a.count);
  });

  private addTransition(key: string, transition: SankeyTransition, map: Map<string, SankeyTransition>): void {
    const existing = map.get(key);
    if (existing) {
      existing.count++;
    } else {
      map.set(key, { ...transition });
    }
  }

  totalApplications = computed(() => this.service.applications().length);

  ngOnInit(): void {
    this.isLoading.set(true);
    this.error.set(null);

    this.service.getApplications().subscribe({
      next: () => {
        this.isLoading.set(false);
        // Defer render until Angular has updated the DOM with the chart container
        afterNextRender(() => this.renderChart(), { injector: this.injector });
      },
      error: (err) => {
        this.error.set('Failed to load applications');
        this.isLoading.set(false);
        console.error(err);
      }
    });
  }

  onBack(): void {
    this.router.navigate(['/applications']);
  }

  getStatusColor(status: SankeyStatus): string {
    return this.statusColors[status];
  }

  private renderChart(): void {
    const container = this.chartContainer()?.nativeElement;
    if (!container) return;

    const transitions = this.transitions();
    if (transitions.length === 0) return;

    // Clear previous render
    d3.select(container).selectAll('*').remove();

    // Dimensions
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };
    const width = container.offsetWidth - margin.left - margin.right;
    const height = 600 - margin.top - margin.bottom;

    // Build unique nodes
    const nodeSet = new Set<string>();
    const nodes: NodeExtra[] = [];

    const ensureNode = (status: SankeyStatus): string => {
      const name = this.formatStatusLabel(status);
      if (!nodeSet.has(name)) {
        nodeSet.add(name);
        nodes.push({ name, status });
      }
      return name;
    };

    // Links reference nodes by name (matching nodeId accessor)
    const links: { source: string; target: string; value: number; count: number }[] = [];
    for (const t of transitions) {
      links.push({
        source: ensureNode(t.from),
        target: ensureNode(t.to),
        value: t.count,
        count: t.count
      });
    }

    // Create sankey layout
    const sankeyLayout = sankey<NodeExtra, LinkExtra>()
      .nodeId((d: SNode) => (d as unknown as NodeExtra).name)
      .nodeWidth(18)
      .nodePadding(24)
      .nodeSort(null)
      .extent([[0, 0], [width, height]]);

    const graph = sankeyLayout({
      nodes: nodes.map(d => ({ ...d })),
      links: links.map(d => ({ ...d }))
    });

    // Create SVG
    const svg = d3.select(container)
      .append('svg')
      .attr('viewBox', `0 0 ${width + margin.left + margin.right} ${height + margin.top + margin.bottom}`)
      .attr('width', '100%')
      .attr('height', height + margin.top + margin.bottom)
      .append('g')
      .attr('transform', `translate(${margin.left},${margin.top})`);

    // Draw links
    svg.append('g')
      .selectAll('path')
      .data(graph.links)
      .join('path')
      .attr('d', sankeyLinkHorizontal())
      .attr('fill', 'none')
      .attr('stroke', (d: SLink) => this.statusColors[(d.source as SNode as unknown as NodeExtra).status])
      .attr('stroke-opacity', 0.3)
      .attr('stroke-width', (d: SLink) => Math.max(1, d.width ?? 0))
      .on('mouseenter', function () {
        d3.select(this).attr('stroke-opacity', 0.55);
      })
      .on('mouseleave', function () {
        d3.select(this).attr('stroke-opacity', 0.3);
      })
      .append('title')
      .text((d: SLink) =>
        `${(d.source as SNode as unknown as NodeExtra).name} → ${(d.target as SNode as unknown as NodeExtra).name}: ${d.value}`
      );

    // Draw nodes
    const node = svg.append('g')
      .selectAll('g')
      .data(graph.nodes)
      .join('g');

    node.append('rect')
      .attr('x', (d: SNode) => d.x0 ?? 0)
      .attr('y', (d: SNode) => d.y0 ?? 0)
      .attr('height', (d: SNode) => Math.max(1, (d.y1 ?? 0) - (d.y0 ?? 0)))
      .attr('width', (d: SNode) => (d.x1 ?? 0) - (d.x0 ?? 0))
      .attr('fill', (d: SNode) => this.statusColors[(d as unknown as NodeExtra).status])
      .attr('rx', 3)
      .append('title')
      .text((d: SNode) => `${(d as unknown as NodeExtra).name}: ${d.value}`);

    // Labels
    node.append('text')
      .attr('x', (d: SNode) => ((d.x0 ?? 0) < width / 2) ? (d.x1 ?? 0) + 8 : (d.x0 ?? 0) - 8)
      .attr('y', (d: SNode) => ((d.y0 ?? 0) + (d.y1 ?? 0)) / 2)
      .attr('dy', '0.35em')
      .attr('text-anchor', (d: SNode) => ((d.x0 ?? 0) < width / 2) ? 'start' : 'end')
      .attr('font-size', '15px')
      .attr('font-weight', '600')
      .attr('fill', '#333')
      .text((d: SNode) => `${(d as unknown as NodeExtra).name} (${d.value})`);
  }

  private formatStatusLabel(status: SankeyStatus): string {
    return status.charAt(0) + status.slice(1).toLowerCase();
  }
}

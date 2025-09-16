"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  HelpCircle,
  MessageSquare,
  Clock,
  CheckCircle,
  Search,
  Eye,
  MessageCircle,
} from "lucide-react";

interface SupportTicket {
  id: string;
  subject: string;
  description: string;
  status: "open" | "in_progress" | "resolved" | "closed";
  priority: "low" | "medium" | "high" | "urgent";
  category:
    | "bug_report"
    | "feature_request"
    | "technical_support"
    | "account_issue"
    | "other";
  user: {
    id: string;
    name: string;
    email: string;
  };
  assignedTo?: string;
  createdAt: string;
  updatedAt: string;
  responses: TicketResponse[];
}

interface TicketResponse {
  id: string;
  message: string;
  author: {
    name: string;
    role: "user" | "admin";
  };
  createdAt: string;
}

const mockTickets: SupportTicket[] = [
  {
    id: "1",
    subject: "Cannot upload files larger than 10MB",
    description:
      "I'm trying to upload a research dataset file but getting an error for files over 10MB. The documentation says 50MB should be supported.",
    status: "open",
    priority: "high",
    category: "technical_support",
    user: {
      id: "user1",
      name: "Dr. Sarah Johnson",
      email: "sarah.j@university.edu",
    },
    createdAt: "2024-01-15T09:30:00Z",
    updatedAt: "2024-01-15T09:30:00Z",
    responses: [],
  },
  {
    id: "2",
    subject: "Feature Request: Batch annotation export",
    description:
      "Would be great to have a way to export multiple annotation files at once instead of downloading them one by one.",
    status: "in_progress",
    priority: "medium",
    category: "feature_request",
    user: {
      id: "user2",
      name: "Prof. Michael Chen",
      email: "m.chen@research.org",
    },
    assignedTo: "Admin Team",
    createdAt: "2024-01-14T14:22:00Z",
    updatedAt: "2024-01-15T08:15:00Z",
    responses: [
      {
        id: "1",
        message:
          "Thanks for the suggestion! We're currently working on implementing batch operations for annotations. This should be available in the next release.",
        author: { name: "Support Team", role: "admin" },
        createdAt: "2024-01-15T08:15:00Z",
      },
    ],
  },
  {
    id: "3",
    subject: "Bug: Annotation positions shifting after save",
    description:
      "After saving annotations, some of the position markers shift slightly from where I placed them. This is causing inconsistencies in my dataset.",
    status: "resolved",
    priority: "high",
    category: "bug_report",
    user: {
      id: "user3",
      name: "Dr. Emily Rodriguez",
      email: "e.rodriguez@lab.com",
    },
    assignedTo: "Technical Team",
    createdAt: "2024-01-13T16:45:00Z",
    updatedAt: "2024-01-14T12:30:00Z",
    responses: [
      {
        id: "2",
        message:
          "We've identified the issue with annotation positioning. The fix has been deployed and should resolve the problem. Please let us know if you continue to experience issues.",
        author: { name: "Technical Team", role: "admin" },
        createdAt: "2024-01-14T12:30:00Z",
      },
    ],
  },
];

const ticketStats = {
  total: 23,
  open: 8,
  inProgress: 5,
  resolved: 7,
  closed: 3,
  avgResponseTime: "4.2 hours",
  satisfaction: 94,
};

export function SupportSystem() {
  const [selectedTicket, setSelectedTicket] = useState<SupportTicket | null>(
    null
  );
  const [isTicketDialogOpen, setIsTicketDialogOpen] = useState(false);
  const [isResponseDialogOpen, setIsResponseDialogOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string>("all");
  const [priorityFilter, setPriorityFilter] = useState<string>("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [responseMessage, setResponseMessage] = useState("");

  const handleViewTicket = (ticket: SupportTicket) => {
    setSelectedTicket(ticket);
    setIsTicketDialogOpen(true);
  };

  const handleRespondToTicket = (ticket: SupportTicket) => {
    setSelectedTicket(ticket);
    setIsResponseDialogOpen(true);
  };

  const handleSendResponse = () => {
    if (selectedTicket && responseMessage.trim()) {
      console.log(
        "Sending response to ticket:",
        selectedTicket.id,
        responseMessage
      );
      setResponseMessage("");
      setIsResponseDialogOpen(false);
      setSelectedTicket(null);
    }
  };

  const handleUpdateStatus = (
    ticketId: string,
    newStatus: SupportTicket["status"]
  ) => {
    console.log("Updating ticket status:", ticketId, newStatus);
  };

  const getStatusBadge = (status: SupportTicket["status"]) => {
    switch (status) {
      case "open":
        return <Badge className="bg-red-100 text-red-800">Open</Badge>;
      case "in_progress":
        return <Badge className="bg-blue-100 text-blue-800">In Progress</Badge>;
      case "resolved":
        return <Badge className="bg-green-100 text-green-800">Resolved</Badge>;
      case "closed":
        return <Badge className="bg-gray-100 text-gray-800">Closed</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const getPriorityBadge = (priority: SupportTicket["priority"]) => {
    switch (priority) {
      case "urgent":
        return <Badge className="bg-red-500 text-white">Urgent</Badge>;
      case "high":
        return <Badge className="bg-orange-100 text-orange-800">High</Badge>;
      case "medium":
        return <Badge className="bg-yellow-100 text-yellow-800">Medium</Badge>;
      case "low":
        return <Badge className="bg-green-100 text-green-800">Low</Badge>;
      default:
        return <Badge variant="outline">Unknown</Badge>;
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const filteredTickets = mockTickets.filter((ticket) => {
    const matchesStatus =
      statusFilter === "all" || ticket.status === statusFilter;
    const matchesPriority =
      priorityFilter === "all" || ticket.priority === priorityFilter;
    const matchesSearch =
      searchQuery === "" ||
      ticket.subject.toLowerCase().includes(searchQuery.toLowerCase()) ||
      ticket.user.name.toLowerCase().includes(searchQuery.toLowerCase());

    return matchesStatus && matchesPriority && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold">Support System</h2>
        <p className="text-muted-foreground">
          Manage user support tickets and inquiries
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <HelpCircle className="h-8 w-8 text-blue-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Total Tickets
                </p>
                <p className="text-2xl font-bold">{ticketStats.total}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-orange-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Open Tickets
                </p>
                <p className="text-2xl font-bold">{ticketStats.open}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Avg Response
                </p>
                <p className="text-2xl font-bold">
                  {ticketStats.avgResponseTime}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <MessageSquare className="h-8 w-8 text-purple-600" />
              <div className="ml-4">
                <p className="text-sm font-medium text-muted-foreground">
                  Satisfaction
                </p>
                <p className="text-2xl font-bold">
                  {ticketStats.satisfaction}%
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Filters and Search */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <MessageSquare className="h-5 w-5 mr-2" />
            Support Tickets
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center space-x-4 mb-6">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                <Input
                  placeholder="Search tickets..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <Select value={statusFilter} onValueChange={setStatusFilter}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Status</SelectItem>
                <SelectItem value="open">Open</SelectItem>
                <SelectItem value="in_progress">In Progress</SelectItem>
                <SelectItem value="resolved">Resolved</SelectItem>
                <SelectItem value="closed">Closed</SelectItem>
              </SelectContent>
            </Select>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-32">
                <SelectValue placeholder="Priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priority</SelectItem>
                <SelectItem value="urgent">Urgent</SelectItem>
                <SelectItem value="high">High</SelectItem>
                <SelectItem value="medium">Medium</SelectItem>
                <SelectItem value="low">Low</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* Tickets List */}
          <div className="space-y-4">
            {filteredTickets.map((ticket) => (
              <div key={ticket.id} className="border rounded-lg p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <h3 className="font-medium">{ticket.subject}</h3>
                      {getStatusBadge(ticket.status)}
                      {getPriorityBadge(ticket.priority)}
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-2">
                      <span>#{ticket.id}</span>
                      <span>{ticket.category.replace("_", " ")}</span>
                      <span>{ticket.user.name}</span>
                      <span>{formatDate(ticket.createdAt)}</span>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {ticket.description.length > 120
                        ? `${ticket.description.substring(0, 120)}...`
                        : ticket.description}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2 ml-4">
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleViewTicket(ticket)}
                    >
                      <Eye className="h-4 w-4 mr-1" />
                      View
                    </Button>
                    <Button
                      variant="outline"
                      size="sm"
                      onClick={() => handleRespondToTicket(ticket)}
                    >
                      <MessageCircle className="h-4 w-4 mr-1" />
                      Respond
                    </Button>
                  </div>
                </div>
              </div>
            ))}

            {filteredTickets.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                No tickets found matching your criteria.
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* View Ticket Dialog */}
      <Dialog open={isTicketDialogOpen} onOpenChange={setIsTicketDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>Support Ticket #{selectedTicket?.id}</DialogTitle>
            <DialogDescription>
              Ticket details and conversation history
            </DialogDescription>
          </DialogHeader>
          {selectedTicket && (
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  {getStatusBadge(selectedTicket.status)}
                  {getPriorityBadge(selectedTicket.priority)}
                </div>
                <Select
                  value={selectedTicket.status}
                  onValueChange={(status: SupportTicket["status"]) =>
                    handleUpdateStatus(selectedTicket.id, status)
                  }
                >
                  <SelectTrigger className="w-32">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="open">Open</SelectItem>
                    <SelectItem value="in_progress">In Progress</SelectItem>
                    <SelectItem value="resolved">Resolved</SelectItem>
                    <SelectItem value="closed">Closed</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div>
                <h3 className="font-medium mb-2">{selectedTicket.subject}</h3>
                <p className="text-sm text-muted-foreground mb-4">
                  Created by {selectedTicket.user.name} on{" "}
                  {formatDate(selectedTicket.createdAt)}
                </p>
                <p className="text-sm">{selectedTicket.description}</p>
              </div>

              {selectedTicket.responses.length > 0 && (
                <div>
                  <h4 className="font-medium mb-2">Responses</h4>
                  <div className="space-y-3">
                    {selectedTicket.responses.map((response) => (
                      <div key={response.id} className="border rounded-lg p-3">
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium">
                            {response.author.name}
                          </span>
                          <span className="text-xs text-muted-foreground">
                            {formatDate(response.createdAt)}
                          </span>
                        </div>
                        <p className="text-sm">{response.message}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsTicketDialogOpen(false)}
            >
              Close
            </Button>
            <Button
              onClick={() => {
                setIsTicketDialogOpen(false);
                if (selectedTicket) handleRespondToTicket(selectedTicket);
              }}
            >
              Respond
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Response Dialog */}
      <Dialog
        open={isResponseDialogOpen}
        onOpenChange={setIsResponseDialogOpen}
      >
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Respond to Ticket</DialogTitle>
            <DialogDescription>
              Send a response to the user for ticket #{selectedTicket?.id}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <Textarea
              placeholder="Type your response..."
              value={responseMessage}
              onChange={(e) => setResponseMessage(e.target.value)}
              rows={5}
            />
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setIsResponseDialogOpen(false)}
            >
              Cancel
            </Button>
            <Button
              onClick={handleSendResponse}
              disabled={!responseMessage.trim()}
            >
              Send Response
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
